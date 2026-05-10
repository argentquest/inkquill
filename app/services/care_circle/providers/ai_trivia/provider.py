import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from app.services.care_circle.variety_utils import pick_avoiding_recent
from typing import Any, Dict


TRIVIA_CATEGORIES = [
    {"key": "daily_life", "hint": "Share a happy fact about everyday home or community life."},
    {"key": "inventions", "hint": "Share a cheerful fact about a useful invention or gadget that became popular during that era."},
    {"key": "entertainment", "hint": "Share a fun fact about a popular film, TV show, radio programme, or entertainer from that time."},
    {"key": "nature_seasons", "hint": "Share a delightful fact about nature, animals, or the seasons as people experienced them back then."},
    {"key": "food_drink", "hint": "Share a warm fact about a popular food, drink, restaurant, or cooking trend from that era."},
    {"key": "sport_leisure", "hint": "Share an uplifting fact about a popular sport, hobby, or leisure activity people enjoyed."},
    {"key": "fashion", "hint": "Share a cheerful fact about fashion, clothing, or style that was popular during that era."},
    {"key": "music", "hint": "Share a delightful fact about the music scene, dance craze, or popular songs from that time."},
    {"key": "travel", "hint": "Share a fascinating fact about how people travelled or went on holiday during that era."},
    {"key": "home_family", "hint": "Share a warm fact about home life, family traditions, or how households were run back then."},
    {"key": "famous_people", "hint": "Share an uplifting fact about a well-known and beloved person from that era — an actor, singer, or public figure."},
    {"key": "community", "hint": "Share a cheerful fact about community spirit, local events, or how neighbours supported each other back then."},
    {"key": "animals_pets", "hint": "Share a delightful fact about a popular animal, beloved pet, or wildlife that people cherished during that time."},
    {"key": "celebrations", "hint": "Share a joyful fact about how people celebrated holidays, birthdays, or special occasions during that era."},
    {"key": "science_wonder", "hint": "Share an amazing but comforting fact about a scientific discovery or space achievement from that time."},
    {"key": "gardens_plants", "hint": "Share a lovely fact about gardening, popular plants, or the joy of growing things during that era."},
    {"key": "crafts_hobbies", "hint": "Share a fun fact about a popular craft, hobby, or pastime that many people enjoyed back then."},
    {"key": "language_words", "hint": "Share a charming fact about a word, phrase, or saying that was popular or newly coined during that era."},
]


class AiTriviaProvider(BaseCareCircleProvider):
    provider_key = "ai_trivia"
    is_safe_for_patient = True

    """
    Provides a daily trivia fact and a music suggestion using a Large Language Model.

    Rotates across six trivia categories (daily life, inventions, entertainment,
    nature/seasons, food/drink, sport/leisure) for day-to-day variety.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = self.get_patient_preferences(patient_profile)
        default_era = cfg.get("default_era", "1950s")
        default_singer = cfg.get("default_singer", "Frank Sinatra")
        era = prefs.get("era_of_youth", default_era)
        singers = prefs.get("favorite_singers") or []
        if not singers and prefs.get("favorite_singer"):
            singers = [prefs["favorite_singer"]]
        patient_id = getattr(patient_profile, "id", None) if patient_profile else None
        singer = pick_avoiding_recent(singers, "ai_trivia_singer", patient_id=patient_id) if singers else default_singer

        category = pick_avoiding_recent(
            TRIVIA_CATEGORIES,
            "ai_trivia_category",
            key_fn=lambda x: x["key"],
        )

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
                f"{category['hint']} Focus on the {era}. "
                f"Also suggest one song by {singer} or a similar artist "
                f"to listen to today. "
                f"Keep each to 1 short sentence. "
                f"Use only well-known, positive, and uplifting facts. "
                f"Avoid obscure, distressing, or controversial topics. "
                f'Return as JSON: {{"trivia": "...", "music": "..."}}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=self.get_system_prompt(patient_profile)
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=self.get_system_prompt(patient_profile),
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
