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



class LocalHistoryProvider(BaseCareCircleProvider):
    provider_key = "local_history"
    is_safe_for_patient = True

    """
    Generates a warm, positive historical fact about the recipient's area.

    Prefers hometown (where they grew up) over city_for_weather. Enriches
    the prompt with era of youth, nationality/background, and life roles
    so the fact feels personally relevant.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        cfg = self.patient_config

        # Prefer hometown (birthplace) over current weather city
        hometown = prefs.get("hometown", "").strip()
        city = prefs.get("city_for_weather", "").strip()
        location = hometown or city

        if not location:
            return {
                "location": "your town",
                "fact": cfg.get(
                    "fallback_text",
                    "Every town has a wonderful history full of kind "
                    "people and happy memories.",
                ),
            }

        era = prefs.get("era_of_youth", "")
        nationality = prefs.get("nationality_or_background", "")
        life_roles = prefs.get("life_roles", [])

        context_parts = []
        if era:
            context_parts.append(
                f"They were young in {location} during the {era}."
            )
        if nationality:
            context_parts.append(
                f"They have a {nationality} background — "
                f"lean into that cultural heritage if relevant."
            )
        if life_roles:
            context_parts.append(
                f"They were a {life_roles[0]} — "
                f"mention something that would resonate with that role."
            )
        context_str = " ".join(context_parts)

        try:
            prompt = (
                f"Write one warm, positive historical fact about {location}. "
                f"2 short sentences only. "
                f"{context_str} "
                f"Focus on something cheerful — a famous landmark, a lovely "
                f"tradition, or something the town is proud of. "
                f"Make it feel like a proud, happy memory. "
                f"Avoid wars, disasters, controversial events, or anything distressing."
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
                return {"location": location, "fact": llm_response.content}
        except Exception:
            pass

        fallback = cfg.get(
            "fallback_text",
            f"{location} is a wonderful place with a rich and happy history.",
        )
        return {"location": location, "fact": fallback}
