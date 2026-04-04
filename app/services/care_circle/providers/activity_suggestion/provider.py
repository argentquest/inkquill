import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict



class ActivitySuggestionProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    Suggests one of the recipient's favourite activities in a warm,
    inviting way. Adapts to mobility level, and weaves in pets,
    favourite foods, and preferred pronoun where relevant.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        name = getattr(patient_profile, 'preferences', {}).get("recipient_name", "friend")
        cfg = self.patient_config

        activities = prefs.get("favorite_activities", [])
        if not activities:
            activities = cfg.get(
                "fallback_activities",
                [
                    "a gentle walk",
                    "listening to music",
                    "sitting in the garden",
                ],
            )

        activity = random.choice(activities)

        mobility_level = prefs.get("mobility_level", "")
        favourite_foods = prefs.get("favourite_foods", [])
        pets = prefs.get("pets", [])
        preferred_pronoun = prefs.get("preferred_pronoun", "")

        context_parts = []
        if mobility_level == "seated":
            context_parts.append(
                "Keep the suggestion seated and very gentle — "
                "no standing or walking required."
            )
        elif mobility_level == "active":
            context_parts.append(
                "They are active and enjoy getting out, so the "
                "suggestion can be a little more lively."
            )
        if favourite_foods:
            context_parts.append(
                f"If the activity involves food or drink, "
                f"{favourite_foods[0]} is a favourite."
            )
        if pets:
            context_parts.append(
                f"They have {pets[0]} — the activity could involve "
                f"their pet if it fits."
            )
        if preferred_pronoun:
            context_parts.append(
                f"Use {preferred_pronoun} pronouns."
            )

        context_str = " ".join(context_parts)

        try:
            prompt = (
                f"Write 2 short sentences gently encouraging {name} to "
                f"enjoy {activity} today. "
                f"Make it feel warm, inviting, and easy — like a lovely "
                f"treat, not a task. "
                f"{context_str}"
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
                return {
                    "activity": activity,
                    "suggestion": llm_response.content,
                }
        except Exception:
            pass

        fallback = cfg.get(
            "fallback_text",
            f"Today would be a lovely day to enjoy {activity}. "
            f"It always brings such joy.",
        )
        return {"activity": activity, "suggestion": fallback}
