"""
Wikimedia Gallery provider for public-domain and freely licensed photographs.
"""

import logging
import random
import re
import unicodedata
from typing import Any, Dict

import httpx

from app.services.care_circle.provider_base import (
    BaseCareCircleProvider,
    WIKIMEDIA_USER_AGENT,
)

logger = logging.getLogger(__name__)

_COMMONS_API = "https://commons.wikimedia.org/w/api.php"

_THEMES = [
    {
        "key": "landscapes",
        "label": "Landscapes",
        "category": "Landscape photographs",
        "tagline": "Beautiful scenery from around the world.",
        "fallback": {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Yosemite_valley_horse-shoe_bend_pano_Luca_Galuzzi_2006.jpg/800px-Yosemite_valley_horse-shoe_bend_pano_Luca_Galuzzi_2006.jpg",
            "title": "Yosemite Valley",
            "description": "A sweeping view of Yosemite's glacier-carved granite walls and forested valley floor.",
            "credit": "Luca Galuzzi / Wikimedia Commons (CC BY-SA 2.5)",
        },
    },
    {
        "key": "animals",
        "label": "Animals",
        "category": "Featured pictures of dogs",
        "tagline": "Wonderful creatures from near and far.",
        "fallback": {
            "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Alaskan%20Malamute%20R%20Bartz.jpg",
            "title": "Alaskan Malamute",
            "description": "A bright, alert dog pauses for a portrait outdoors.",
            "credit": "Wikimedia Commons (featured picture)",
        },
    },
    {
        "key": "flowers",
        "label": "Flowers",
        "category": "Flowers",
        "tagline": "Nature's most colourful blooms.",
        "fallback": {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg/800px-Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg",
            "title": "Water Lilies",
            "description": "Monet's beloved water lilies float peacefully on a sunlit garden pond.",
            "credit": "Claude Monet / Wikimedia Commons (public domain)",
        },
    },
    {
        "key": "gardens",
        "label": "Gardens",
        "category": "Featured pictures of gardens",
        "tagline": "Peaceful green spaces to enjoy.",
        "fallback": {
            "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Boston%20Public%20Garden%20%2836008p%29.jpg",
            "title": "Boston Public Garden",
            "description": "A graceful city garden offers flowers, trees, and a peaceful path to enjoy.",
            "credit": "Wikimedia Commons (featured picture)",
        },
    },
    {
        "key": "sunsets",
        "label": "Sunsets & Skies",
        "category": "Sunsets",
        "tagline": "Golden skies and peaceful evenings.",
        "fallback": {
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/USA_10791_Grand_Canyon_Luca_Galuzzi_2007.jpg/800px-USA_10791_Grand_Canyon_Luca_Galuzzi_2007.jpg",
            "title": "Grand Canyon at Dusk",
            "description": "Warm evening light paints the canyon walls in shades of red, orange, and gold.",
            "credit": "Luca Galuzzi / Wikimedia Commons (CC BY-SA 2.5)",
        },
    },
]

_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif")


def _strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _latin_ratio(text: str) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 1.0
    latin_letters = [char for char in letters if "LATIN" in unicodedata.name(char, "")]
    return len(latin_letters) / len(letters)


def _looks_english_friendly(title: str, description: str) -> bool:
    combined = " ".join(part for part in [title, description] if part).strip()
    if not combined:
        return False
    return _latin_ratio(combined) >= 0.85


class WikimediaGalleryProvider(BaseCareCircleProvider):
    provider_key = "wikimedia_gallery"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        themes = cfg.get("themes", _THEMES)
        theme = random.choice(themes)
        preferred_language = str(
            getattr(patient_profile, "preferred_language", "")
            or cfg.get("preferred_language")
            or "en"
        ).lower()
        require_english_friendly = preferred_language.startswith("en")

        try:
            async with httpx.AsyncClient(
                timeout=12.0,
                headers={"User-Agent": WIKIMEDIA_USER_AGENT},
            ) as client:
                list_resp = await client.get(
                    _COMMONS_API,
                    params={
                        "action": "query",
                        "list": "categorymembers",
                        "cmtitle": f"Category:{theme['category']}",
                        "cmlimit": "500",
                        "cmtype": "file",
                        "format": "json",
                    },
                )
                list_resp.raise_for_status()
                members = list_resp.json().get("query", {}).get("categorymembers", [])

                image_members = [
                    member
                    for member in members
                    if member.get("title", "").lower().endswith(_IMAGE_EXTS)
                ]
                if not image_members:
                    raise ValueError(
                        f"No image files found in category '{theme['category']}'"
                    )

                candidates = random.sample(image_members, k=min(len(image_members), 12))

                for chosen in candidates:
                    payload = await self._fetch_candidate_payload(client, chosen, theme)
                    if not payload:
                        continue
                    if not require_english_friendly:
                        return payload
                    if _looks_english_friendly(
                        payload["title"],
                        payload["description"],
                    ):
                        return payload

                raise ValueError(
                    f"No language-appropriate image metadata found in category '{theme['category']}'"
                )

        except Exception as exc:
            logger.warning("WikimediaGalleryProvider failed (%s) - using fallback.", exc)

        fb = theme["fallback"]
        return {
            "image_url": fb["image_url"],
            "title": fb["title"],
            "description": fb["description"],
            "credit": fb["credit"],
            "theme_label": theme["label"],
            "theme_tagline": theme["tagline"],
        }

    async def _fetch_candidate_payload(
        self,
        client: httpx.AsyncClient,
        chosen: dict[str, Any],
        theme: dict[str, Any],
    ) -> Dict[str, Any] | None:
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
            return None

        extmeta = imageinfo.get("extmetadata", {})
        raw_title = extmeta.get("ObjectName", {}).get("value", "")
        raw_desc = extmeta.get("ImageDescription", {}).get("value", "")
        raw_artist = extmeta.get("Artist", {}).get("value", "")
        license_name = extmeta.get("LicenseShortName", {}).get("value", "")

        title = _strip_html(raw_title) or chosen["title"].replace("File:", "").rsplit(".", 1)[0]
        description = _strip_html(raw_desc)
        artist = _strip_html(raw_artist)

        credit_parts = [artist] if artist else []
        credit_parts.append("Wikimedia Commons")
        if license_name:
            credit_parts.append(f"({license_name})")
        credit = " / ".join(part for part in credit_parts if part)

        return {
            "image_url": image_url,
            "title": title,
            "description": description,
            "credit": credit,
            "theme_label": theme["label"],
            "theme_tagline": theme["tagline"],
        }
