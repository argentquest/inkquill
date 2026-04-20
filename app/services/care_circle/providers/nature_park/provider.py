"""
Nature Park provider — U.S. National Park Service Open Data API.

Fetches a random public-domain photograph from a random National Park,
including the image, park name, image caption, and credit.

Requires NPS_API_KEY (free registration at https://www.nps.gov/subjects/developer/get-started.htm).
Falls back to a curated list of hardcoded park images when the key is absent or the API is unavailable.
"""

import logging
import random
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.services.care_circle.provider_base import BaseCareCircleProvider, WIKIMEDIA_USER_AGENT

logger = logging.getLogger(__name__)

_NPS_PARKS_URL = "https://developer.nps.gov/api/v1/parks"

# Curated fallback images — verified accessible Wikimedia Commons public-domain photographs.
# URLs were confirmed via the Wikimedia imageinfo API (pre-generated thumbnail sizes that
# are served from the CDN without hotlinking restrictions).
# Used when NPS_API_KEY is absent or the API is unavailable.
_FALLBACK_IMAGES = [
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Yosemite_Valley_from_Tunnel_View.jpg/960px-Yosemite_Valley_from_Tunnel_View.jpg",
        "park_name": "Yosemite National Park",
        "title": "Valley View at Tunnel View",
        "caption": "El Capitan and Half Dome frame the sweeping Yosemite Valley on a clear day.",
        "credit": "Wikimedia Commons (public domain)",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Half_Dome_from_Glacier_Point_2013.jpg/960px-Half_Dome_from_Glacier_Point_2013.jpg",
        "park_name": "Yosemite National Park",
        "title": "Half Dome from Glacier Point",
        "caption": "The famous granite dome rises above the valley under a brilliant blue sky.",
        "credit": "Wikimedia Commons (public domain)",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Grand_Canyon_view_from_Pima_Point_2010.jpg/960px-Grand_Canyon_view_from_Pima_Point_2010.jpg",
        "park_name": "Grand Canyon National Park",
        "title": "View from Pima Point",
        "caption": "Layers of red and orange rock stretch for miles under a wide, open sky.",
        "credit": "Wikimedia Commons (public domain)",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Grand_Prismatic_Spring_2013.jpg/960px-Grand_Prismatic_Spring_2013.jpg",
        "park_name": "Yellowstone National Park",
        "title": "Grand Prismatic Spring",
        "caption": "Vivid rings of blue, green, yellow, and orange circle the steaming thermal pool.",
        "credit": "Wikimedia Commons (public domain)",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Bass_Harbor_Head_Light_Station_2016.jpg/960px-Bass_Harbor_Head_Light_Station_2016.jpg",
        "park_name": "Acadia National Park",
        "title": "Bass Harbor Head Lighthouse",
        "caption": "A classic New England lighthouse perches on rocky pink granite above the Atlantic.",
        "credit": "Wikimedia Commons (public domain)",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Bryce_Canyon_Amphitheater_Hoodoos_Panorama.jpg/960px-Bryce_Canyon_Amphitheater_Hoodoos_Panorama.jpg",
        "park_name": "Bryce Canyon National Park",
        "title": "Amphitheater Hoodoos",
        "caption": "Thousands of orange and red spire-shaped rock formations glow in the morning light.",
        "credit": "Wikimedia Commons (public domain)",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Capitol_Reef_National_Park.jpg/960px-Capitol_Reef_National_Park.jpg",
        "park_name": "Capitol Reef National Park",
        "title": "Waterpocket Fold",
        "caption": "Colorful cliffs and canyon walls wind through this hidden gem of southern Utah.",
        "credit": "Wikimedia Commons (public domain)",
    },
    {
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Great_Smoky_Mountains_National_Park.jpg/960px-Great_Smoky_Mountains_National_Park.jpg",
        "park_name": "Great Smoky Mountains National Park",
        "title": "Morning in the Smokies",
        "caption": "Soft morning fog drifts through layers of blue-green ridges at sunrise.",
        "credit": "Wikimedia Commons (public domain)",
    },
]


class NatureParkProvider(BaseCareCircleProvider):
    provider_key = "nature_park"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Fetch a random National Park photograph via the NPS Open Data API.

        Strategy:
        1. Retrieve up to 500 parks (with their images) from the NPS parks endpoint.
        2. Filter to parks that have at least one image.
        3. Pick a random park, then a random image from that park.
        4. Return the image URL, park name, title, caption, and credit.

        If NPS_API_KEY is not configured or the API call fails, a hardcoded
        fallback image is returned instead.
        """
        api_key: str | None = getattr(settings, "NPS_API_KEY", None)

        if not api_key:
            logger.info("NPS_API_KEY not configured — using fallback nature park image.")
            return self._random_fallback()

        try:
            async with httpx.AsyncClient(timeout=12.0, headers={"User-Agent": WIKIMEDIA_USER_AGENT}) as client:
                resp = await client.get(
                    _NPS_PARKS_URL,
                    params={
                        "limit": 500,
                        "fields": "images",
                        "api_key": api_key,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            parks = data.get("data", [])
            parks_with_images = [p for p in parks if p.get("images")]
            if not parks_with_images:
                raise ValueError("No parks with images returned from NPS API")

            park = random.choice(parks_with_images)
            image = random.choice(park["images"])

            image_url: str = image.get("url", "")
            if not image_url:
                raise ValueError("Selected image has no URL")

            return {
                "image_url": image_url,
                "park_name": park.get("fullName", "National Park"),
                "title": image.get("title", ""),
                "caption": image.get("caption") or image.get("altText", ""),
                "credit": image.get("credit", "National Park Service"),
            }

        except Exception as exc:
            logger.warning("NatureParkProvider API failed (%s) — using fallback image.", exc)
            return self._random_fallback()

    def _random_fallback(self) -> Dict[str, Any]:
        cfg = self.patient_config
        fallback_images = cfg.get("fallback_images", _FALLBACK_IMAGES)
        return dict(random.choice(fallback_images))
