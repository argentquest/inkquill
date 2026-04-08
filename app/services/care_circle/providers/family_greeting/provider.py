import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict



class FamilyGreetingProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Generates a warm, imagined short note 'from' one of the recipient's
    family members.

    Enriches the message with life roles, pets, favourite foods, and
    hometown so each letter feels genuinely personal.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        recipient = getattr(patient_profile, 'preferences', {}).get("recipient_name", "friend")
        family_members = prefs.get("family_members", [])
        cfg = self.patient_config

        if not family_members:
            return {
                "sender": "Your family",
                "message": cfg.get(
                    "fallback_text",
                    f"We are all thinking of you today, {recipient}. "
                    f"You are so loved.",
                ),
            }

        sender = random.choice(family_members)

        life_roles = prefs.get("life_roles", [])
        pets = prefs.get("pets", [])
        favourite_foods = prefs.get("favourite_foods", [])
        hometown = prefs.get("hometown", "")

        context_parts = []
        if life_roles:
            context_parts.append(
                f"{recipient} was a wonderful {life_roles[0]} — "
                f"the sender can acknowledge that lovingly."
            )
        if pets:
            context_parts.append(
                f"Mention {pets[0]} warmly if it fits naturally."
            )
        if favourite_foods:
            context_parts.append(
                f"You could reference {recipient}'s love of "
                f"{favourite_foods[0]} to make it personal."
            )
        if hometown:
            context_parts.append(
                f"They are from {hometown} — a gentle nod to home is lovely."
            )
        context_str = " ".join(context_parts)

        try:
            prompt = (
                f"Write a short, loving note from {sender} to {recipient}. "
                f"2 sentences only. "
                f"Make it feel warm, caring, and full of love. "
                f"Write in first person as {sender}. "
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
                return {"sender": sender, "message": llm_response.content}
        except Exception:
            pass

        fallback = cfg.get(
            "fallback_text",
            f"Thinking of you today, {recipient}. You are so loved.",
        )
        return {"sender": sender, "message": fallback}
