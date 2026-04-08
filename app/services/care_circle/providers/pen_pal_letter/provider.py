"""
Pen Pal Letter provider.

Generates a warm, fictional short letter (80–100 words) written as if
from an old dear friend. Addressed to the resident by name, mentions
the current season, a nostalgic shared memory, and ends with one gentle
question to spark a happy recollection.
"""

import datetime
import random

import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


_SEASON_MAP = {
    12: "winter", 1: "winter", 2: "winter",
    3: "spring",  4: "spring", 5: "spring",
    6: "summer",  7: "summer", 8: "summer",
    9: "autumn",  10: "autumn", 11: "autumn",
}


class PenPalLetterProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Pen Pal Letter — a warm fictional letter from an old friend.

    Personalised with the resident's name, era, activities, hometown,
    life roles, pets, favourite foods and TV shows when available.
    Falls back to static letters from config if LLM is unavailable.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        name = getattr(patient_profile, 'preferences', {}).get("recipient_name", "Dear Friend")
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        era = prefs.get("era_of_youth", "1950s")

        # Prefer favorite_activities over the old 'interests' field
        activities = (
            prefs.get("favorite_activities")
            or prefs.get("hobbies")
            or []
        )
        hometown = prefs.get("hometown", "")
        life_roles = prefs.get("life_roles", [])
        pets = prefs.get("pets", [])
        favourite_foods = prefs.get("favourite_foods", [])
        favourite_tv_shows = prefs.get("favourite_tv_shows", [])

        month = datetime.date.today().month
        season = _SEASON_MAP.get(month, "spring")

        friend_names = cfg.get("friend_names", ["Margaret"])
        friend_name = random.choice(friend_names)

        # Build optional context lines to enrich the letter
        context_parts = []
        if activities:
            context_parts.append(
                f"They love {' and '.join(activities[:2])}."
            )
        if hometown:
            context_parts.append(
                f"They grew up in {hometown} — mention it warmly."
            )
        if life_roles:
            context_parts.append(
                f"They were a wonderful {life_roles[0]}."
            )
        if pets:
            context_parts.append(
                f"They have {pets[0]} — you can mention it affectionately."
            )
        if favourite_foods:
            context_parts.append(
                f"A favourite food of theirs is {favourite_foods[0]}."
            )
        if favourite_tv_shows:
            context_parts.append(
                f"They used to love watching {favourite_tv_shows[0]}."
            )
        context_str = " ".join(context_parts)

        try:
            prompt = (
                f"Write a short, warm pen pal letter (80–100 words) to {name}.\n"
                f"Write it AS IF you are {friend_name}, an old dear friend "
                f"from the {era}.\n"
                f"Mention something lovely about the current season ({season}) — "
                f"a sight, smell, or simple pleasure.\n"
                f"Reference one warm shared memory from the {era}.\n"
                f"{context_str}\n"
                f"End with one gentle question inviting a happy recollection.\n"
                f"Tone: warm, familiar, simple, nostalgic. "
                f"Do NOT mention illness, care homes, or memory problems.\n"
                f"Start with 'Dear {name},' and sign off "
                f"'With love, {friend_name}'"
            )
            llm_response = await generate_text_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                llm_response, prompt=prompt, system_prompt=DEMENTIA_SYSTEM_PROMPT
            )
            if llm_response.content and len(llm_response.content) > 40:
                return {
                    "letter": llm_response.content,
                    "friend_name": friend_name,
                }
        except Exception as e:
            app_logger.error(f"LLM Error (pen_pal_letter): {e}")

        fallback_letters = cfg.get("fallback_letters", [])
        if fallback_letters:
            letter = random.choice(fallback_letters)
            letter = (
                letter
                .replace("{name}", name)
                .replace("{friend}", friend_name)
                .replace("{season}", season)
                .replace("{era}", era)
            )
            return {"letter": letter, "friend_name": friend_name}

        return {
            "letter": (
                f"Dear {name},\n\n"
                f"I have been thinking of you so fondly lately. "
                f"The {season} air reminds me of the happy times we used "
                f"to share. "
                f"Do you remember the fun we had back in those wonderful "
                f"{era} days? "
                f"I hope you are keeping well and smiling as always.\n\n"
                f"With love, {friend_name}"
            ),
            "friend_name": friend_name,
        }
