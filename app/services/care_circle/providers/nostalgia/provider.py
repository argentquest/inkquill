import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from typing import Any, Dict


NOSTALGIA_TOPICS = [
    {
        "key": "food",
        "hint": (
            "Focus on a popular food, meal, or treat that people enjoyed back then — "
            "something from a kitchen, bakery, or family dinner table."
        ),
    },
    {
        "key": "music_dance",
        "hint": (
            "Focus on the music or dancing from that era — "
            "a dance style, a radio show, a favourite song, or a jukebox."
        ),
    },
    {
        "key": "neighbourhood",
        "hint": (
            "Focus on neighbourhood life — a corner shop, children playing outside, "
            "a street game, or a familiar community gathering."
        ),
    },
    {
        "key": "fashion",
        "hint": (
            "Focus on fashion or style from that time — "
            "clothing, hairstyles, hats, or getting dressed up for a special occasion."
        ),
    },
    {
        "key": "entertainment",
        "hint": (
            "Focus on entertainment from that era — "
            "a favourite TV or radio show, a cinema trip, or a popular game."
        ),
    },
    {
        "key": "school_or_work",
        "hint": (
            "Focus on school days or everyday working life from that time — "
            "a classroom memory, a lunch break, or a simple daily routine."
        ),
    },
]


class NostalgiaProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Generates personalized nostalgic memories using a Large Language Model.

    Rotates across six topic areas (food, music/dance, neighbourhood, fashion,
    entertainment, school/work) to bring different warm memories each day.
    Personalises with nationality, hometown, life roles, favourite foods and
    TV shows when available.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        default_era = cfg.get("default_era", "1950s")
        era = prefs.get("era_of_youth", default_era) or default_era
        name = getattr(patient_profile, 'preferences', {}).get("recipient_name", "friend")

        nationality = prefs.get("nationality_or_background", "")
        hometown = prefs.get("hometown", "")
        life_roles = prefs.get("life_roles", [])
        favourite_foods = prefs.get("favourite_foods", [])
        favourite_tv_shows = prefs.get("favourite_tv_shows", [])

        topic = random.choice(NOSTALGIA_TOPICS)

        # Build optional context lines to enrich the prompt
        context_parts = []
        if nationality:
            context_parts.append(f"They have a {nationality} background.")
        if hometown:
            context_parts.append(f"They grew up in {hometown}.")
        if life_roles:
            context_parts.append(
                f"They were a {', '.join(life_roles[:2])}."
            )
        if topic["key"] == "food" and favourite_foods:
            context_parts.append(
                f"Foods they loved: {', '.join(favourite_foods[:2])}."
            )
        if topic["key"] == "entertainment" and favourite_tv_shows:
            context_parts.append(
                f"Shows they enjoyed: {', '.join(favourite_tv_shows[:2])}."
            )
        context_str = " ".join(context_parts)

        try:
            prompt = (
                f"Write a happy memory from the {era} for {name}. "
                f"{topic['hint']} "
                f"{context_str} "
                f"Keep it to 2 short sentences. Make it feel cozy and familiar."
            )
            llm_response = await generate_text_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if llm_response.content and len(llm_response.content) > 10:
                return {"nostalgia": llm_response.content}
        except Exception as e:
            app_logger.error(f"LLM Error (nostalgia): {e}")

        facts = cfg.get("facts", {})
        fallback = cfg.get(
            "fallback",
            "Do you remember the wonderful music and dances from your youth?",
        )
        era_facts = facts.get(era, [fallback])
        if isinstance(era_facts, list):
            return {"nostalgia": random.choice(era_facts)}
        return {"nostalgia": era_facts}
