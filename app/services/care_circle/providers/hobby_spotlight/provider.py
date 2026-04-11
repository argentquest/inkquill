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


class HobbySpotlightProvider(BaseCareCircleProvider):
    provider_key = "hobby_spotlight"
    is_safe_for_patient = True

    """
    Generates a warm, personal story about one of the recipient's hobbies.

    Enriches the prompt with life roles, hometown, era of youth, and
    nationality/background when available.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        name = getattr(patient_profile, 'preferences', {}).get("recipient_name", "friend")
        hobbies = prefs.get("hobbies", [])
        cfg = self.patient_config

        if not hobbies:
            hobbies = cfg.get(
                "fallback_hobbies", ["gardening", "reading", "knitting"]
            )

        hobby = random.choice(hobbies)

        life_roles = prefs.get("life_roles", [])
        hometown = prefs.get("hometown", "")
        era = prefs.get("era_of_youth", "")
        nationality = prefs.get("nationality_or_background", "")

        context_parts = []
        if life_roles:
            context_parts.append(
                f"They were a {life_roles[0]} — let that shine through."
            )
        if hometown:
            context_parts.append(
                f"They grew up in {hometown} — you can tie the hobby to that place."
            )
        if era:
            context_parts.append(
                f"They were young in the {era} — reference that time if it fits."
            )
        if nationality:
            context_parts.append(
                f"They have a {nationality} background."
            )
        context_str = " ".join(context_parts)

        try:
            prompt = (
                f"Write 2 short, warm sentences about {name} and their love "
                f"of {hobby}. "
                f"{context_str} "
                f"Make it feel personal, cozy, and joyful. "
                f"Do not ask questions. Just describe how lovely {hobby} is. "
                f"Do not mention illness, health problems, or care situations. "
                f"Keep the content simple and universally understandable."
            )
            llm_response = await generate_text_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                llm_response, prompt=prompt, system_prompt=DEMENTIA_SYSTEM_PROMPT
            )
            if llm_response.content and len(llm_response.content) > 10:
                return {"hobby": hobby, "story": llm_response.content}
        except Exception:
            pass

        fallback = cfg.get(
            "fallback_text",
            f"{hobby} is such a wonderful thing to enjoy.",
        )
        return {"hobby": hobby, "story": fallback}
