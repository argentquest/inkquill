"""
Seasonal Poem provider for Care Circle patient sessions.
Uses an LLM to generate a short, cheerful poem about the current season.
Falls back to a curated static pool if LLM is unavailable.
"""

import random
import logging
import datetime
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_json_with_usage,
)

logger = logging.getLogger(__name__)


def _current_season() -> str:
    month = datetime.date.today().month
    if month in (12, 1, 2):
        return "winter"
    elif month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    else:
        return "autumn"


FALLBACK_POEMS = {
    "spring": [
        {
            "title": "Spring Has Come",
            "lines": (
                "The flowers are waking from their sleep,\n"
                "And colour fills the air;\n"
                "The bluebirds sing and robin calls,\n"
                "Spring is everywhere."
            ),
        },
        {
            "title": "A Spring Morning",
            "lines": (
                "The rain has washed the world so clean,\n"
                "The grass is fresh and bright;\n"
                "The cherry blossoms open wide,\n"
                "What a beautiful sight."
            ),
        },
    ],
    "summer": [
        {
            "title": "A Sunny Day",
            "lines": (
                "The sun shines warm on field and lane,\n"
                "The bees hum soft and low;\n"
                "The roses bloom beside the path,\n"
                "With a gentle, golden glow."
            ),
        },
        {
            "title": "Summer Afternoon",
            "lines": (
                "Beneath the shade of an old oak tree,\n"
                "The afternoon drifts by;\n"
                "A gentle breeze, a lemonade,\n"
                "And a wide and cloudless sky."
            ),
        },
    ],
    "autumn": [
        {
            "title": "Autumn Gold",
            "lines": (
                "The leaves are turning red and gold,\n"
                "They drift so soft and slow;\n"
                "The harvest moon hangs in the sky,\n"
                "With a warm and amber glow."
            ),
        },
        {
            "title": "October Walk",
            "lines": (
                "The crisp air carries a woody smell,\n"
                "Of apples, leaves, and rain;\n"
                "The world has dressed in rust and red,\n"
                "Before the cold sets in again."
            ),
        },
    ],
    "winter": [
        {
            "title": "Winter Peace",
            "lines": (
                "A blanket of white covers the ground,\n"
                "The world is still and deep;\n"
                "The holly berries shine like fire,\n"
                "As the meadows lie asleep."
            ),
        },
        {
            "title": "By the Fire",
            "lines": (
                "The frost is tapping at the pane,\n"
                "The kettle softly sings;\n"
                "Come sit beside the glowing fire,\n"
                "And enjoy the warmth it brings."
            ),
        },
    ],
}


class SeasonalPoemProvider(BaseCareCircleProvider):
    provider_key = "seasonal_poem"
    is_safe_for_patient = True

    """
    Generates a short, warm poem about the current season using an LLM.
    Falls back to a curated static pool of 8 seasonal poems (2 per season).
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        season = _current_season()

        try:
            prompt = (
                f"Write a short, gentle {season} poem for a senior person. "
                f"It should be 4 lines long, cheerful and warm, with a simple rhyme scheme. "
                f"The poem should paint a peaceful {season} scene using familiar, comforting imagery. "
                f"Keep the language simple and beautiful — no complex words. "
                f"Return as JSON: "
                '{"title": "...", "lines": "line1\\nline2\\nline3\\nline4"}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(llm_response, prompt=prompt, system_prompt=DEMENTIA_SYSTEM_PROMPT)
            if data.get("title") and data.get("lines"):
                return {
                    "title": data["title"],
                    "lines": data["lines"],
                    "season": season.capitalize(),
                }
        except Exception as e:
            logger.error(f"LLM Error (seasonal_poem): {e}")

        fallback_pool = FALLBACK_POEMS.get(season, FALLBACK_POEMS["spring"])
        entry = random.choice(fallback_pool)
        return {
            "title": entry["title"],
            "lines": entry["lines"],
            "season": season.capitalize(),
        }
