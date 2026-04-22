"""
Base classes for comic strip providers.

BaseComicStripProvider   — common payload structure, shared template directory
WikimediaComicProvider   — fetches a random image from a Wikimedia Commons category,
                           seeded by date + patient_id for per-patient variety
"""

from __future__ import annotations

import logging
import random
import re
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from app.services.care_circle.provider_base import BaseCareCircleProvider, WIKIMEDIA_USER_AGENT

logger = logging.getLogger(__name__)

_COMMONS_API = "https://commons.wikimedia.org/w/api.php"
_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif")

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    return _HTML_TAG_RE.sub("", text).strip() if text else ""


class BaseComicStripProvider(BaseCareCircleProvider):
    """
    All comic strip providers inherit from this class.

    Subclasses must set:
        provider_key      — unique key, e.g. "comic_abe_martin"
        comic_name        — display name shown in the newsletter
        comic_author      — creator / rights-holder
        comic_license     — short licence string, e.g. "Public Domain"
        comic_attribution — full attribution line required by the licence

    And implement:
        _fetch_strip(for_date, patient_id) → dict with keys:
            image_url, caption, attribution (optional override), source_url
    """

    comic_name: str = "Comic Strip"
    comic_author: str = ""
    comic_license: str = "Public Domain"
    comic_attribution: str = ""
    is_safe_for_patient: bool = True

    @property
    def template_dir(self) -> Path:
        return Path(__file__).parent / "comic_templates"

    def _date_seed(self, for_date: date, patient_id: int = 0) -> int:
        """Deterministic seed per patient per day — different image for each patient."""
        return for_date.toordinal() * 100_000 + patient_id * 1000 + sum(ord(c) for c in self.provider_key)

    async def _fetch_strip(self, for_date: date, patient_id: int = 0) -> dict[str, Any]:
        raise NotImplementedError

    async def _generate_payload(self, patient_profile: Any) -> dict[str, Any]:
        today = self.get_generation_date()
        patient_id = int(getattr(patient_profile, "id", 0) or 0)
        strip = await self._fetch_strip(today, patient_id)
        now = self.get_generation_datetime()
        return {
            "title": self.comic_name,
            "author": self.comic_author,
            "license": self.comic_license,
            "comic_date": today.strftime("%B %d, %Y"),
            "generated_at": now.strftime("%B %d, %Y at %I:%M %p"),
            "image_url": strip.get("image_url", ""),
            "caption": strip.get("caption", ""),
            "attribution": strip.get("attribution") or self.comic_attribution,
            "source_url": strip.get("source_url", ""),
        }


class WikimediaComicProvider(BaseComicStripProvider):
    """
    Fetches a random image from a Wikimedia Commons category.

    Subclasses must set:
        wikimedia_category  — category name without "Category:" prefix
    """

    wikimedia_category: str = ""

    async def _fetch_strip(self, for_date: date, patient_id: int = 0) -> dict[str, Any]:
        rng = random.Random(self._date_seed(for_date, patient_id))

        try:
            async with httpx.AsyncClient(
                timeout=12.0,
                headers={"User-Agent": WIKIMEDIA_USER_AGENT},
            ) as client:
                # Step 1 — list files in category
                list_resp = await client.get(
                    _COMMONS_API,
                    params={
                        "action": "query",
                        "list": "categorymembers",
                        "cmtitle": f"Category:{self.wikimedia_category}",
                        "cmlimit": "500",
                        "cmtype": "file",
                        "format": "json",
                    },
                )
                list_resp.raise_for_status()
                members = list_resp.json().get("query", {}).get("categorymembers", [])
                image_members = [
                    m for m in members
                    if m.get("title", "").lower().endswith(_IMAGE_EXTS)
                ]
                if not image_members:
                    raise ValueError(f"No image files in category '{self.wikimedia_category}'")

                chosen = rng.choice(image_members)

                # Step 2 — fetch image URL + metadata
                info_resp = await client.get(
                    _COMMONS_API,
                    params={
                        "action": "query",
                        "titles": chosen["title"],
                        "prop": "imageinfo",
                        "iiprop": "url|extmetadata",
                        "iiurlwidth": "800",
                        "format": "json",
                    },
                )
                info_resp.raise_for_status()
                pages = info_resp.json().get("query", {}).get("pages", {})
                page = next(iter(pages.values()), {})
                imageinfo = (page.get("imageinfo") or [{}])[0]

                image_url = imageinfo.get("thumburl") or imageinfo.get("url", "")
                if not image_url:
                    raise ValueError(f"No image URL for {chosen['title']}")

                extmeta = imageinfo.get("extmetadata", {})
                artist = _clean(extmeta.get("Artist", {}).get("value", ""))
                license_name = _clean(extmeta.get("LicenseShortName", {}).get("value", ""))
                description = _clean(extmeta.get("ImageDescription", {}).get("value", ""))

                author_credit = artist or self.comic_author
                attribution_parts = [author_credit, "Wikimedia Commons"]
                if license_name:
                    attribution_parts.append(f"({license_name})")

                source_url = (
                    "https://commons.wikimedia.org/wiki/"
                    + chosen["title"].replace(" ", "_")
                )

                return {
                    "image_url": image_url,
                    "caption": description[:200] if description else "",
                    "attribution": " / ".join(p for p in attribution_parts if p),
                    "source_url": source_url,
                }

        except Exception as exc:
            logger.warning("%s: Wikimedia fetch failed (%s), using fallback", self.provider_key, exc)
            return self._fallback_strip()

    def _fallback_strip(self) -> dict[str, Any]:
        fallback_images = self.patient_config.get("fallback_images", [])
        if fallback_images:
            import random
            image_url = random.choice(fallback_images)
            return {
                "image_url": image_url,
                "caption": f"Today's {self.comic_name}",
                "attribution": self.comic_attribution,
                "source_url": "https://mimiandeunice.com",
            }
        return {
            "image_url": "",
            "caption": f"Today's {self.comic_name}",
            "attribution": self.comic_attribution,
            "source_url": f"https://commons.wikimedia.org/wiki/Category:{self.wikimedia_category}",
        }
