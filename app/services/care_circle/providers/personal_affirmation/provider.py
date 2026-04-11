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



class PersonalAffirmationProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Generates a deeply personal affirmation using the recipient's name,
    activities, life roles, preferred pronoun, and pets.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        name = getattr(patient_profile, 'preferences', {}).get("recipient_name", "friend")
        cfg = self.patient_config

        activities = prefs.get("favorite_activities", [])
        life_roles = prefs.get("life_roles", [])
        preferred_pronoun = prefs.get("preferred_pronoun", "")
        pets = prefs.get("pets", [])

        context_parts = [f"Use their name ({name}) at least once."]

        if activities:
            activity = random.choice(activities)
            context_parts.append(
                f"Reference their love of {activity}."
            )
        if life_roles:
            context_parts.append(
                f"Acknowledge what a wonderful {life_roles[0]} they are/were."
            )
        if pets:
            context_parts.append(
                f"You may mention {pets[0]} warmly."
            )
        if preferred_pronoun:
            context_parts.append(
                f"Use {preferred_pronoun} pronouns."
            )

        context_str = " ".join(context_parts)

        try:
            prompt = (
                f"Write a personal, loving affirmation for {name}. "
                f"2 short sentences only. "
                f"{context_str} "
                f"Make it feel warm, specific, and uplifting."
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
                return {"name": name, "affirmation": llm_response.content}
        except Exception:
            pass

        fallback = cfg.get(
            "fallback_text",
            f"{name}, you are loved and you bring joy to everyone around you.",
        )
        return {"name": name, "affirmation": fallback}
