"""
GNews provider — GNews.io REST API for news article search and top headlines.

Fetches news articles via the GNews API (search and top-headlines endpoints),
with support for language, country, and category filtering. Returns structured
article data suitable for newsletter rendering.

Requires GNEWS_API_KEY (free registration at https://gnews.io/).
Falls back to a curated list of hardcoded news stories when the key is absent
or the API is unavailable.
"""

import hashlib
import logging
import time
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.services.care_circle.provider_base import BaseCareCircleProvider, WIKIMEDIA_USER_AGENT
from app.utils.iso_codes import COUNTRIES

logger = logging.getLogger(__name__)

_GNEWS_BASE_URL = "https://gnews.io/api/v4"
_GNEWS_SEARCH_URL = f"{_GNEWS_BASE_URL}/search"
_GNEWS_HEADLINES_URL = f"{_GNEWS_BASE_URL}/top-headlines"

# Supported GNews categories
SUPPORTED_CATEGORIES = [
    "general", "world", "nation", "business",
    "technology", "entertainment", "sports", "science", "health",
]

# Curated fallback news stories — used when API key is absent or API is unavailable.
_FALLBACK_STORIES = [
    {
        "title": "Community Volunteers Plant Trees in Local Park",
        "description": "Residents came together to plant dozens of trees, making the neighborhood greener and more welcoming for families.",
        "url": "#",
        "image": "",
        "publishedAt": "2026-04-19T08:00:00Z",
        "source": {"name": "Local News", "url": "#"},
    },
    {
        "title": "New Library Program Brings Books to Seniors",
        "description": "A new delivery service ensures that homebound seniors can enjoy fresh books and magazines every week.",
        "url": "#",
        "image": "",
        "publishedAt": "2026-04-18T10:00:00Z",
        "source": {"name": "Community Herald", "url": "#"},
    },
    {
        "title": "Scientists Discover New Species of Butterfly",
        "description": "Researchers have identified a beautiful new butterfly species in a tropical forest, adding to our understanding of nature.",
        "url": "#",
        "image": "",
        "publishedAt": "2026-04-17T14:00:00Z",
        "source": {"name": "Science Daily", "url": "#"},
    },
    {
        "title": "Town Celebrates Annual Harvest Festival",
        "description": "Families gathered for food, music, and fun at the yearly harvest celebration that brings the community together.",
        "url": "#",
        "image": "",
        "publishedAt": "2026-04-16T09:00:00Z",
        "source": {"name": "Town Gazette", "url": "#"},
    },
    {
        "title": "Garden Club Shares Tips for Spring Planting",
        "description": "Local gardening experts share their best advice for growing flowers and vegetables this spring season.",
        "url": "#",
        "image": "",
        "publishedAt": "2026-04-15T07:00:00Z",
        "source": {"name": "Garden Weekly", "url": "#"},
    },
]

def _split_location(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _build_local_query(
    *,
    configured_query: str,
    weather_city: str,
    hometown: str,
    country_code: str,
    language: str,
) -> str:
    def _clean(query: str) -> str:
        return " ".join((query or "").split()).strip()

    location = weather_city or hometown
    location_parts = _split_location(location)
    city = location_parts[0] if location_parts else ""
    country_name = COUNTRIES.get((country_code or "").upper(), country_code or "")

    if city:
        if language.lower().startswith("fr"):
            return _clean(f"{city} nouvelles locales")
        return _clean(f"{city} local news")

    if country_name:
        if language.lower().startswith("fr"):
            return _clean(f"{country_name} nouvelles")
        return _clean(f"{country_name} news")

    return _clean(configured_query)


def _build_country_query(*, configured_query: str, country_code: str, language: str) -> str:
    def _clean(query: str) -> str:
        return " ".join((query or "").split()).strip()

    country_name = COUNTRIES.get((country_code or "").upper(), country_code or "")
    if country_name:
        if language.lower().startswith("fr"):
            return _clean(f"{country_name} nouvelles")
        return _clean(f"{country_name} news")

    return _clean(configured_query)


class GnewsProvider(BaseCareCircleProvider):
    """
    Fetches news articles from the GNews API.

    Supports two modes:
    - search: keyword-based article search (default, for city/topic queries)
    - top-headlines: top headlines by category and country

    The provider normalizes GNews responses into a provider-neutral article schema
    and supports caching, deduplication, and rate-limit awareness.

    Language and country are read from the patient profile (preferred_language, country)
    when not explicitly overridden by provider config.
    """

    provider_key = "gnews"
    is_safe_for_patient = True

    # Simple in-memory cache: key -> (timestamp, articles)
    _cache: Dict[str, tuple[float, List[Dict[str, Any]]]] = {}

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Fetch news articles from GNews API.

        Configuration options (from config.json and patient_config):
        - mode: "search" (default) or "top-headlines"
        - query: search query string (for search mode)
        - lang: language code (e.g., "en", "fr") — falls back to patient_profile.preferred_language
        - country: country code (e.g., "us", "ca") — falls back to patient_profile.country
        - category: topic category (for top-headlines mode)
        - max: number of articles to return (default 5)
        - cache_ttl: cache time-to-live in seconds (default 600)

        Returns:
            dict with "articles" list and "source" metadata.
        """
        cfg = self.patient_config
        api_key: Optional[str] = getattr(settings, "GNEWS_API_KEY", None)

        if not api_key:
            logger.info("GNEWS_API_KEY not configured — using fallback news stories.")
            return self._build_payload(self._fallback_stories())

        mode = cfg.get("mode", "search")
        prefs = self.get_patient_preferences(patient_profile)

        # Read language and country from patient profile when not in config
        lang = cfg.get("lang") or getattr(patient_profile, "preferred_language", None) or "en"
        country = cfg.get("country") or getattr(patient_profile, "country", None) or "us"
        lang = str(lang).lower()
        country = str(country).lower()
        weather_city = str(prefs.get("city_for_weather") or "").strip()
        hometown = str(prefs.get("hometown") or "").strip()

        max_articles = min(cfg.get("max", 5), 100)  # GNews max per request
        cache_ttl = cfg.get("cache_ttl", 600)  # 10 minutes default

        # Build cache key
        cache_key = self._build_cache_key(mode, lang, country, cfg, max_articles)

        # Check cache first
        cached = self._get_cached(cache_key, cache_ttl)
        if cached is not None:
            logger.info("GNews: returning cached results for key %s", cache_key[:32])
            return self._build_payload(cached)

        try:
            articles: List[Dict[str, Any]] = []

            if mode == "top-headlines":
                articles = await self._fetch_headlines(api_key, lang, country, cfg, max_articles)
            else:
                articles = await self._fetch_localized_search(
                    api_key,
                    lang,
                    country,
                    cfg,
                    max_articles,
                    weather_city=weather_city,
                    hometown=hometown,
                )

            # Deduplicate by URL
            articles = self._deduplicate(articles)

            # Cache results
            self._set_cached(cache_key, articles)

            return self._build_payload(articles)

        except Exception as exc:
            logger.warning("GNews API failed (%s) — using fallback stories.", exc)
            return self._build_payload(self._fallback_stories())

    async def _fetch_localized_search(
        self,
        api_key: str,
        lang: str,
        country: str,
        cfg: Dict[str, Any],
        max_articles: int,
        *,
        weather_city: str,
        hometown: str,
    ) -> List[Dict[str, Any]]:
        configured_query = cfg.get("query", "news")
        local_query = _build_local_query(
            configured_query=configured_query,
            weather_city=weather_city,
            hometown=hometown,
            country_code=country,
            language=lang,
        )
        logger.info("GNews: using localized query %r", local_query)
        local_articles = await self._fetch_search(
            api_key,
            lang,
            country,
            {**cfg, "query": local_query},
            max_articles,
        )
        if local_articles:
            return local_articles

        country_query = _build_country_query(
            configured_query=configured_query,
            country_code=country,
            language=lang,
        )
        logger.info("GNews: local query empty, falling back to country query %r", country_query)
        return await self._fetch_search(
            api_key,
            lang,
            country,
            {**cfg, "query": country_query},
            max_articles,
        )

    async def _fetch_search(
        self,
        api_key: str,
        lang: str,
        country: str,
        cfg: Dict[str, Any],
        max_articles: int,
    ) -> List[Dict[str, Any]]:
        """Fetch articles via GNews search endpoint."""
        query = cfg.get("query", "news")
        params: Dict[str, Any] = {
            "q": query,
            "lang": lang,
            "max": max_articles,
            "token": api_key,
        }
        if country:
            params["country"] = country

        category = cfg.get("category")
        if category and category in SUPPORTED_CATEGORIES:
            params["category"] = category

        async with httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": WIKIMEDIA_USER_AGENT},
        ) as client:
            resp = await client.get(_GNEWS_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        return data.get("articles", [])

    async def _fetch_headlines(
        self,
        api_key: str,
        lang: str,
        country: str,
        cfg: Dict[str, Any],
        max_articles: int,
    ) -> List[Dict[str, Any]]:
        """Fetch top headlines via GNews top-headlines endpoint."""
        params: Dict[str, Any] = {
            "lang": lang,
            "max": max_articles,
            "token": api_key,
        }
        if country:
            params["country"] = country

        category = cfg.get("category")
        if category and category in SUPPORTED_CATEGORIES:
            params["category"] = category

        async with httpx.AsyncClient(
            timeout=15.0,
            headers={"User-Agent": WIKIMEDIA_USER_AGENT},
        ) as client:
            resp = await client.get(_GNEWS_HEADLINES_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        return data.get("articles", [])

    def _build_payload(self, raw_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize raw GNews articles into provider-neutral schema."""
        articles = []
        for raw in raw_articles:
            article = self._normalize_article(raw)
            if article:
                articles.append(article)

        return {
            "articles": articles,
            "source": "GNews",
        }

    def _normalize_article(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize a single GNews article into the provider-neutral schema.

        Fields:
        - id: stable ID (hashed from URL)
        - title: article title
        - description: short summary
        - content: full article content (if available)
        - url: article URL
        - image_url: image/thumbnail URL
        - published_at: ISO 8601 timestamp
        - source_name: source publication name
        - source_url: source URL
        - provider: "gnews"
        """
        title = (raw.get("title") or "").strip()
        if not title:
            return None

        url = raw.get("url") or "#"
        source = raw.get("source") or {}
        source_name = (source.get("name") or "").strip() or "Unknown Source"
        source_url = source.get("url") or ""

        # Generate stable ID from URL
        article_id = hashlib.sha256(url.encode()).hexdigest()[:16]

        return {
            "id": article_id,
            "title": title,
            "description": (raw.get("description") or "").strip() or title,
            "content": (raw.get("content") or "").strip(),
            "url": url,
            "image_url": raw.get("image") or "",
            "published_at": raw.get("publishedAt") or "",
            "source_name": source_name,
            "source_url": source_url,
            "provider": "gnews",
        }

    def _deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate articles by URL (primary) or title+source (fallback)."""
        seen_urls = set()
        seen_hashes = set()
        unique = []

        for article in articles:
            url = article.get("url", "")
            if url and url != "#" and url in seen_urls:
                continue
            if url and url != "#":
                seen_urls.add(url)
                unique.append(article)
                continue

            # Fallback: hash of title + source_name
            fallback_hash = hashlib.md5(
                f"{article.get('title', '')}|{article.get('source_name', '')}".encode()
            ).hexdigest()
            if fallback_hash in seen_hashes:
                continue
            seen_hashes.add(fallback_hash)
            unique.append(article)

        return unique

    def _build_cache_key(
        self,
        mode: str,
        lang: str,
        country: str,
        cfg: Dict[str, Any],
        max_articles: int,
    ) -> str:
        """Build a cache key from query parameters."""
        parts = [mode, lang, country, str(max_articles)]
        if mode == "search":
            parts.append(cfg.get("query", ""))
        category = cfg.get("category", "")
        if category:
            parts.append(category)
        return "|".join(parts)

    def _get_cached(
        self, cache_key: str, cache_ttl: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached results if still valid."""
        cached = self._cache.get(cache_key)
        if cached is None:
            return None
        timestamp, articles = cached
        if time.time() - timestamp > cache_ttl:
            del self._cache[cache_key]
            return None
        return articles

    def _set_cached(self, cache_key: str, articles: List[Dict[str, Any]]) -> None:
        """Store results in cache."""
        self._cache[cache_key] = (time.time(), articles)

    def _fallback_stories(self) -> List[Dict[str, Any]]:
        """Return curated fallback news stories."""
        cfg = self.patient_config
        fallback = cfg.get("fallback_stories", _FALLBACK_STORIES)
        max_articles = cfg.get("max", 5)
        return fallback[:max_articles]
