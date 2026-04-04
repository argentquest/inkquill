import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


TRIVIA_CATEGORIES = [
    {
        "key": "daily_life",
        "hint": "Share a happy fact about everyday home or community life.",
    },
    {
        "key": "inventions",
        "hint": (
            "Share a cheerful fact about a useful invention or gadget "
            "that became popular during that era."
        ),
    },
    {
        "key": "entertainment",
        "hint": (
            "Share a fun fact about a popular film, TV show, radio programme, "
            "or entertainer from that time."
        ),
    },
    {
        "key": "nature_seasons",
        "hint": (
            "Share a delightful fact about nature, animals, or the seasons "
            "as people experienced them back then."
        ),
    },
    {
        "key": "food_drink",
        "hint": (
            "Share a warm fact about a popular food, drink, restaurant, "
            "or cooking trend from that era."
        ),
    },
    {
        "key": "sport_leisure",
        "hint": (
            "Share an uplifting fact about a popular sport, hobby, "
            "or leisure activity people enjoyed."
        ),
    },
]


class AiTriviaProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    Provides a daily trivia fact and a music suggestion using a Large Language Model.

    Rotates across six trivia categories (daily life, inventions, entertainment,
    nature/seasons, food/drink, sport/leisure) for day-to-day variety.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        default_era = cfg.get("default_era", "1950s")
        default_singer = cfg.get("default_singer", "Frank Sinatra")
        era = prefs.get("era_of_youth", default_era)
        singers = prefs.get("favorite_singers") or []
        if not singers and prefs.get("favorite_singer"):
            singers = [prefs["favorite_singer"]]
        singer = random.choice(singers) if singers else default_singer

        category = random.choice(TRIVIA_CATEGORIES)

        try:
            prompt = (
                f"{category['hint']} Focus on the {era}. "
                f"Also suggest one song by {singer} or a similar artist "
                f"to listen to today. "
                f"Keep each to 1 short sentence. "
                f'Return as JSON: {{"trivia": "...", "music": "..."}}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if data.get("trivia") and data.get("music"):
                return data
        except Exception as e:
            app_logger.error(f"LLM Error (ai_trivia): {e}")

        return {
            "trivia": cfg.get(
                "fallback_trivia",
                f"Remembering the wonderful inventions of the {era}.",
            ),
            "music": cfg.get(
                "fallback_music",
                f"Consider listening to {singer} today.",
            ).format(singer=singer),
        }
