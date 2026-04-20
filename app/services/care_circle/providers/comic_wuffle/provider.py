from app.services.care_circle.comic_base_provider import BaseComicStripProvider
from datetime import date
from typing import Any
import random


class ComicWuffleProvider(BaseComicStripProvider):
    provider_key = "comic_wuffle"
    comic_name = "Wuffle Comics"
    comic_author = "Piti Yindee"
    comic_license = "CC0"
    comic_attribution = "Wuffle Comics by Piti Yindee (CC0)"
    is_safe_for_patient = True

    # Stable CC0-hosted Wuffle pages on Wikimedia Commons.
    _sample_strips = [
        {
            "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Piti%20Yindee%20-%20Wuffle%20-%20Little%20Red%20Riding%20Hood%20%282016%29%20-%20Page%201.jpg",
            "caption": "Wuffle Little Red Riding Hood, page 1.",
            "source_url": "https://commons.wikimedia.org/wiki/File:Piti_Yindee_-_Wuffle_-_Little_Red_Riding_Hood_(2016)_-_Page_1.jpg"
        },
        {
            "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Piti%20Yindee%20-%20Wuffle%20-%20Little%20Red%20Riding%20Hood%20%282016%29%20-%20Page%202.jpg",
            "caption": "Wuffle Little Red Riding Hood, page 2.",
            "source_url": "https://commons.wikimedia.org/wiki/File:Piti_Yindee_-_Wuffle_-_Little_Red_Riding_Hood_(2016)_-_Page_2.jpg"
        },
    ]

    async def _fetch_strip(self, for_date: date, patient_id: int = 0) -> dict[str, Any]:
        """Return a gentle Wuffle comic. Uses deterministic selection per patient/day."""
        seed = for_date.toordinal() * 100 + patient_id % 100
        rng = random.Random(seed)
        return rng.choice(self._sample_strips)
