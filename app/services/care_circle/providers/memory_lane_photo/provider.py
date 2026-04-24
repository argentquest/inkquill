"""
Memory Lane Photo provider — personalised historical photograph.

Uses the patient's profile (era_of_youth, hometown, nationality_or_background,
hobbies) to build a Wikimedia Commons search query via the LLM, fetches a
matching public-domain photograph, then asks the LLM to write a warm,
personalised caption tying the image back to the patient's life.

Falls back to a curated static pool if either the API or LLM calls fail.
"""

import logging
import random
import re
from typing import Any, Dict

import httpx

from app.services.care_circle.provider_base import BaseCareCircleProvider, WIKIMEDIA_USER_AGENT
from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_json_with_usage,
)

logger = logging.getLogger(__name__)

_COMMONS_API = "https://commons.wikimedia.org/w/api.php"
_IMAGE_EXTS = (".jpg", ".jpeg", ".png")
_GENERIC_RESULT_TERMS = {
    "collage",
    "montage",
    "logo",
    "icon",
    "poster",
    "cover",
    "map",
    "seal",
    "flag",
}
_PHOTO_SUBJECT_HINTS = (
    "street scene",
    "neighborhood",
    "market",
    "park",
    "garden",
    "everyday life",
)


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def _normalize_terms(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in re.findall(r"[a-z0-9]+", (value or "").lower()):
            if len(token) >= 3:
                tokens.add(token)
    return tokens


def _split_location(location: str) -> list[str]:
    parts = [
        re.sub(r"\s+", " ", part).strip()
        for part in re.split(r"[,/]", location or "")
    ]
    return [part for part in parts if part]


def _normalize_era_phrase(era: str) -> tuple[str, str]:
    era_text = str(era or "").strip()
    if not era_text:
        return "", ""

    digits = re.sub(r"[^0-9]", "", era_text)
    if len(digits) >= 4:
        year = digits[:4]
        decade = year[:3] + "0s"
        return year, decade

    return era_text, era_text


def _build_search_queries(
    *,
    llm_query: str,
    hometown: str,
    era: str,
    theme: str,
    background: str,
    hobbies_str: str,
) -> list[str]:
    candidates: list[str] = []

    def _add(value: str) -> None:
        cleaned = re.sub(r"\s+", " ", value or "").strip(" ,")
        if cleaned and cleaned not in candidates:
            candidates.append(cleaned)

    location_parts = _split_location(hometown)
    primary_location = location_parts[0] if location_parts else ""
    broader_location = " ".join(location_parts[:2]).strip()
    year, decade = _normalize_era_phrase(era)

    _add(llm_query)

    for subject in _PHOTO_SUBJECT_HINTS:
        if primary_location and decade:
            _add(f"{primary_location} {subject} {decade}")
        if primary_location and year:
            _add(f"{primary_location} {subject} {year}")
        if broader_location and decade:
            _add(f"{broader_location} {subject} {decade}")

    if primary_location and decade:
        _add(f"{primary_location} old photo {decade}")
        _add(f"{primary_location} historic photo {decade}")

    if broader_location and decade:
        _add(f"{broader_location} historic neighborhood {decade}")

    if primary_location and background and decade:
        _add(f"{primary_location} {background} community {decade}")

    if primary_location and hobbies_str and decade:
        first_hobby = hobbies_str.split(",")[0].strip()
        if first_hobby:
            _add(f"{primary_location} {first_hobby} {decade}")

    if theme:
        _add(theme)

    if primary_location:
        _add(primary_location)
    if broader_location and broader_location != primary_location:
        _add(broader_location)
    if decade:
        _add(decade)
    elif year:
        _add(year)

    return candidates


def _score_candidate(
    title: str,
    description: str,
    *,
    query_terms: set[str],
    theme_terms: set[str],
    hometown_terms: set[str],
    era_terms: set[str],
) -> int:
    haystack_terms = _normalize_terms(title, description)
    score = 0

    score += len(haystack_terms & query_terms) * 4
    score += len(haystack_terms & theme_terms) * 3
    score += len(haystack_terms & hometown_terms) * 6
    score += len(haystack_terms & era_terms) * 2

    if haystack_terms & _GENERIC_RESULT_TERMS:
        score -= 8

    return score


def _has_required_relevance(
    score: int,
    *,
    title: str,
    description: str,
    hometown_terms: set[str],
    query_terms: set[str],
) -> bool:
    haystack_terms = _normalize_terms(title, description)

    if hometown_terms and (haystack_terms & hometown_terms):
        return True

    # Without a direct hometown match, require a stronger overlap with the
    # intended query so we avoid drifting to unrelated era-only images.
    return score >= 6 and len(haystack_terms & query_terms) >= 2


# Curated fallback pool used when the API or LLM is unavailable
_FALLBACK_PHOTOS = [
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/800px-A_small_cup_of_coffee.JPG",
        "description": "A quiet morning cup of coffee — the simple pleasures that make a day feel just right.",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Yosemite_valley_horse-shoe_bend_pano_Luca_Galuzzi_2006.jpg/800px-Yosemite_valley_horse-shoe_bend_pano_Luca_Galuzzi_2006.jpg",
        "description": "A peaceful countryside landscape, the kind of view that stays with you for a lifetime.",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg/800px-Orange_tabby_cat_sitting_on_fallen_leaves-Hisashi-01A.jpg",
        "description": "A contented cat resting among autumn leaves — a scene of simple, happy days.",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/GoldenGateBridge-001.jpg/800px-GoldenGateBridge-001.jpg",
        "description": "A grand bridge standing tall against the sky — a reminder of the places we have loved.",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/24701-nature-natural-beauty.jpg/800px-24701-nature-natural-beauty.jpg",
        "description": "A beautiful garden in full bloom, just like the ones we used to tend with such care.",
    },
]


async def _search_wikimedia(query: str) -> list[dict]:
    """Search Wikimedia Commons File namespace. Returns a list of file title dicts."""
    async with httpx.AsyncClient(timeout=12.0, headers={"User-Agent": WIKIMEDIA_USER_AGENT}) as client:
        resp = await client.get(
            _COMMONS_API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srnamespace": "6",
                "srlimit": "20",
                "format": "json",
            },
        )
        resp.raise_for_status()
        results = resp.json().get("query", {}).get("search", [])
        return [r for r in results if r.get("title", "").lower().endswith(_IMAGE_EXTS)]


async def _fetch_image_info(title: str) -> dict:
    """Fetch thumbnail URL and metadata for a single Wikimedia file."""
    async with httpx.AsyncClient(timeout=12.0, headers={"User-Agent": WIKIMEDIA_USER_AGENT}) as client:
        resp = await client.get(
            _COMMONS_API,
            params={
                "action": "query",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url|extmetadata",
                "iiurlwidth": "800",
                "format": "json",
            },
        )
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()), {})
        info = (page.get("imageinfo") or [{}])[0]
        extmeta = info.get("extmetadata", {})
        return {
            "image_url": info.get("thumburl") or info.get("url", ""),
            "raw_title": _strip_html(extmeta.get("ObjectName", {}).get("value", "")),
            "raw_description": _strip_html(extmeta.get("ImageDescription", {}).get("value", "")),
        }


async def _choose_best_match(
    results: list[dict],
    *,
    search_query: str,
    theme: str,
    hometown: str,
    era: str,
) -> dict:
    query_terms = _normalize_terms(search_query)
    theme_terms = _normalize_terms(theme)
    hometown_terms = _normalize_terms(hometown)
    era_terms = _normalize_terms(era)

    best_info: dict | None = None
    best_score = -10_000

    for result in results[:8]:
        info = await _fetch_image_info(result["title"])
        image_url = info.get("image_url", "")
        if not image_url:
            continue

        score = _score_candidate(
            f"{result.get('title', '')} {info.get('raw_title', '')}",
            info.get("raw_description", ""),
            query_terms=query_terms,
            theme_terms=theme_terms,
            hometown_terms=hometown_terms,
            era_terms=era_terms,
        )
        if score > best_score:
            best_score = score
            best_info = {
                **info,
                "_search_title": result.get("title", ""),
                "_score": score,
            }

    if not best_info:
        raise ValueError("No valid Wikimedia image candidates")

    if not _has_required_relevance(
        best_info["_score"],
        title=f"{best_info.get('_search_title', '')} {best_info.get('raw_title', '')}",
        description=best_info.get("raw_description", ""),
        hometown_terms=hometown_terms,
        query_terms=query_terms,
    ):
        raise ValueError("Wikimedia candidates were too generic for the patient context")

    return best_info


class MemoryLanePhotoProvider(BaseCareCircleProvider):
    provider_key = "memory_lane_photo"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        prefs = self.get_patient_preferences(patient_profile)
        patient_name = self.get_recipient_name(patient_profile)

        era = prefs.get("era_of_youth") or "mid-20th century"
        hometown = prefs.get("hometown") or ""
        background = prefs.get("nationality_or_background") or ""
        hobbies = prefs.get("hobbies") or []
        hobbies_str = ", ".join(hobbies[:4]) if hobbies else ""

        # ── Step 1: LLM generates a Wikimedia search query ──────────────────
        try:
            query_prompt = (
                f"Create a short Wikimedia Commons image search query (3–6 words) to find a "
                f"nostalgic historical photograph suited to this person:\n"
                f"- Era of youth: {era}\n"
                f"- Hometown / region: {hometown or 'not specified'}\n"
                f"- Background: {background or 'not specified'}\n"
                f"- Hobbies: {hobbies_str or 'not specified'}\n\n"
                f"The query should find a warm, safe, public-domain image from that era — "
                f"a street scene, garden, market, countryside, or everyday life photograph. "
                f"Avoid famous landmarks or political content.\n"
                f'Return ONLY valid JSON: {{"search_query": "...", "theme": "...short description of what the photo should show..."}}'
            )
            query_data, query_llm_response = await generate_json_with_usage(
                query_prompt, system=DEMENTIA_SYSTEM_PROMPT, max_tokens=256, temperature=0.7
            )
            self.log_llm_response(query_llm_response)
            search_query = (query_data.get("search_query") or "").strip()
            theme = (query_data.get("theme") or "").strip()

            if not search_query:
                raise ValueError("LLM returned empty search_query")

            logger.info("memory_lane_photo: LLM search query = %r (theme: %s)", search_query, theme)
        except Exception as exc:
            logger.warning("memory_lane_photo: LLM query generation failed: %s", exc)
            return _random_fallback()

        # ── Step 2: Search Wikimedia Commons ────────────────────────────────
        try:
            query_candidates = _build_search_queries(
                llm_query=search_query,
                hometown=hometown,
                era=str(era),
                theme=theme,
                background=background,
                hobbies_str=hobbies_str,
            )

            info = None
            last_error: Exception | None = None
            for query_candidate in query_candidates:
                results = await _search_wikimedia(query_candidate)
                if not results:
                    continue
                try:
                    info = await _choose_best_match(
                        results,
                        search_query=query_candidate,
                        theme=theme,
                        hometown=hometown,
                        era=str(era),
                    )
                    search_query = query_candidate
                    break
                except Exception as exc:
                    last_error = exc

            if info is None:
                if last_error is not None:
                    raise last_error
                raise ValueError("No Wikimedia results")

            image_url = info["image_url"]
            if not image_url:
                raise ValueError("No image URL returned")
        except Exception as exc:
            logger.warning("memory_lane_photo: Wikimedia fetch failed: %s", exc)
            return _random_fallback()

        # ── Step 3: LLM writes a warm personalised caption ──────────────────
        try:
            caption_prompt = (
                f"Write a short, warm 1–2 sentence caption for a historical photograph shown "
                f"to {patient_name}, a senior person who grew up in {era}"
                f"{' in ' + hometown if hometown else ''}. "
                f"The image is described as: \"{info['raw_description'] or info['raw_title'] or search_query}\". "
                f"Connect it gently to their life — their era, hometown, or interests ({hobbies_str or 'everyday life'}). "
                f"Keep it warm, simple, and nostalgic. No medical references.\n"
                f'Return ONLY valid JSON: {{"caption": "..."}}'
            )
            caption_data, llm_resp = await generate_json_with_usage(
                caption_prompt, system=DEMENTIA_SYSTEM_PROMPT, max_tokens=200, temperature=0.8
            )
            self.log_llm_response(llm_resp)
            caption = (caption_data.get("caption") or "").strip()
            if not caption:
                raise ValueError("empty caption")
        except Exception as exc:
            logger.warning("memory_lane_photo: LLM caption failed: %s", exc)
            caption = (
                info["raw_description"]
                or f"A nostalgic scene from the {era} — a little piece of the world as it once was."
            )

        return {
            "image_url": image_url,
            "description": caption,
            "search_query": search_query,
            "theme": theme,
        }


def _random_fallback() -> dict:
    entry = random.choice(_FALLBACK_PHOTOS)
    logger.info("memory_lane_photo: using fallback photo")
    return {"image_url": entry["image_url"], "description": entry["description"]}
