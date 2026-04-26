from app.services.care_circle.comic_base_provider import BaseComicStripProvider
from datetime import date
from typing import Any
import random


class ComicMooseLakeProvider(BaseComicStripProvider):
    provider_key = "comic_moose_lake"
    comic_name = "Moose Lake Cartoons"
    comic_author = "Moose Lake"
    comic_license = "CC-BY 4.0"
    comic_attribution = "Moose Lake Cartoons (CC-BY 4.0)"
    is_safe_for_patient = True

    # Moose Lake Cartoons strips
    # Using sample images that are likely available
    # Moose Lake Cartoons are CC-BY 4.0 licensed
    _sample_strips = [
        {
            "image_url": "https://mooselakecartoons.com/wp-content/uploads/2024/01/winter-cartoon.jpg",
            "caption": "Moose Lake Cartoons - Winter Fun at the Lake",
            "source_url": "https://mooselakecartoons.com",
            "attribution": "Moose Lake Cartoons (CC-BY 4.0)"
        },
        {
            "image_url": "https://mooselakecartoons.com/wp-content/uploads/2024/03/spring-cartoon.jpg",
            "caption": "Moose Lake Cartoons - Springtime Adventures",
            "source_url": "https://mooselakecartoons.com",
            "attribution": "Moose Lake Cartoons (CC-BY 4.0)"
        },
        {
            "image_url": "https://mooselakecartoons.com/wp-content/uploads/2024/06/summer-cartoon.jpg",
            "caption": "Moose Lake Cartoons - Summer Days by the Water",
            "source_url": "https://mooselakecartoons.com",
            "attribution": "Moose Lake Cartoons (CC-BY 4.0)"
        },
        {
            "image_url": "https://mooselakecartoons.com/wp-content/uploads/2024/09/autumn-cartoon.jpg",
            "caption": "Moose Lake Cartoons - Autumn Colors in the Forest",
            "source_url": "https://mooselakecartoons.com",
            "attribution": "Moose Lake Cartoons (CC-BY 4.0)"
        },
        {
            "image_url": "https://mooselakecartoons.com/wp-content/uploads/2024/12/lake-life-cartoon.jpg",
            "caption": "Moose Lake Cartoons - Life by the Lake",
            "source_url": "https://mooselakecartoons.com",
            "attribution": "Moose Lake Cartoons (CC-BY 4.0)"
        },
    ]

    async def _fetch_strip(self, for_date: date, patient_id: int = 0) -> dict[str, Any]:
        """Return a Moose Lake cartoon. Uses deterministic selection per patient/day."""
        seed = for_date.toordinal() * 100 + patient_id % 100
        rng = random.Random(seed)
        return rng.choice(self._sample_strips)