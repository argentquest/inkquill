from app.services.care_circle.comic_base_provider import BaseComicStripProvider
from datetime import date
from typing import Any
import random


class ComicPepperCarrotProvider(BaseComicStripProvider):
    provider_key = "comic_pepper_carrot"
    comic_name = "Pepper & Carrot"
    comic_author = "David Revoy"
    comic_license = "CC-BY 4.0"
    comic_attribution = "Pepper & Carrot by David Revoy (CC-BY 4.0)"
    is_safe_for_patient = True

    # Sample Pepper & Carrot strips
    # Using actual episode images from the website
    # Pepper & Carrot is CC-BY 4.0 licensed by David Revoy
    _sample_strips = [
        {
            "image_url": "https://www.peppercarrot.com/0_sources/0_originals/0_fullsize/ep01_the-beginning.jpg",
            "caption": "Pepper & Carrot Episode 1: The Beginning",
            "source_url": "https://www.peppercarrot.com/en/article391/episode-1-the-beginning.html",
            "attribution": "Pepper & Carrot by David Revoy (CC-BY 4.0)"
        },
        {
            "image_url": "https://www.peppercarrot.com/0_sources/0_originals/0_fullsize/ep02_the-garden.jpg",
            "caption": "Pepper & Carrot Episode 2: The Garden",
            "source_url": "https://www.peppercarrot.com/en/article392/episode-2-the-garden.html",
            "attribution": "Pepper & Carrot by David Revoy (CC-BY 4.0)"
        },
        {
            "image_url": "https://www.peppercarrot.com/0_sources/0_originals/0_fullsize/ep03_the-market.jpg",
            "caption": "Pepper & Carrot Episode 3: The Market",
            "source_url": "https://www.peppercarrot.com/en/article393/episode-3-the-market.html",
            "attribution": "Pepper & Carrot by David Revoy (CC-BY 4.0)"
        },
        {
            "image_url": "https://www.peppercarrot.com/0_sources/0_originals/0_fullsize/ep04_the-storm.jpg",
            "caption": "Pepper & Carrot Episode 4: The Storm",
            "source_url": "https://www.peppercarrot.com/en/article394/episode-4-the-storm.html",
            "attribution": "Pepper & Carrot by David Revoy (CC-BY 4.0)"
        },
        {
            "image_url": "https://www.peppercarrot.com/0_sources/0_originals/0_fullsize/ep05_the-discovery.jpg",
            "caption": "Pepper & Carrot Episode 5: The Discovery",
            "source_url": "https://www.peppercarrot.com/en/article395/episode-5-the-discovery.html",
            "attribution": "Pepper & Carrot by David Revoy (CC-BY 4.0)"
        },
    ]

    async def _fetch_strip(self, for_date: date, patient_id: int = 0) -> dict[str, Any]:
        """Return a Pepper & Carrot comic. Uses deterministic selection per patient/day."""
        seed = for_date.toordinal() * 100 + patient_id % 100
        rng = random.Random(seed)
        return rng.choice(self._sample_strips)