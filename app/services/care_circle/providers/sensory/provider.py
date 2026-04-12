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


SENSORY_MODES = [
    {
        "key": "hearing",
        "prompt_hint": (
            "Suggest something soothing to listen to — music, birdsong, "
            "rain on a window, or a familiar voice."
        ),
    },
    {
        "key": "touch",
        "prompt_hint": (
            "Suggest something comforting to feel — a soft fabric, "
            "warm water on their hands, or gentle sunshine on their face."
        ),
    },
    {
        "key": "smell",
        "prompt_hint": (
            "Suggest something pleasant to smell — fresh bread, "
            "a flower, tea, or something from the garden."
        ),
    },
    {
        "key": "taste",
        "prompt_hint": (
            "Suggest something enjoyable to taste — a warm drink, "
            "a piece of fruit, or a favourite biscuit."
        ),
    },
    {
        "key": "sight",
        "prompt_hint": (
            "Suggest something calming to look at — a view out the window, "
            "a favourite photo, a candle flame, or colourful flowers."
        ),
    },
]


class SensoryProvider(BaseCareCircleProvider):
    provider_key = "sensory"
    is_safe_for_patient = True

    """
    Suggests a simple grounding or sensory activity for the user.

    Rotates across all five senses (hearing, touch, smell, taste, sight).
    Personalises with favourite singers, foods, pets, hometown, and
    mobility level when available.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = self.get_patient_preferences(patient_profile)
        name = self.get_recipient_name(patient_profile, default="friend")

        default_singer = cfg.get("default_singer", "Frank Sinatra")
        singers = prefs.get("favorite_singers") or []
        if not singers and prefs.get("favorite_singer"):
            singers = [prefs["favorite_singer"]]
        singer = random.choice(singers) if singers else default_singer

        favourite_foods = prefs.get("favourite_foods", [])
        pets = prefs.get("pets", [])
        hometown = prefs.get("hometown", "")
        mobility_level = prefs.get("mobility_level", "")

        mode = random.choice(SENSORY_MODES)

        # Build sense-specific personal context
        extra_parts = []
        if mode["key"] == "hearing":
            extra_parts.append(f"They enjoy music by {singer}.")
        if mode["key"] == "taste" and favourite_foods:
            extra_parts.append(
                f"A food they love is {random.choice(favourite_foods)}."
            )
        if mode["key"] == "touch" and pets:
            extra_parts.append(
                f"They have {pets[0]} — stroking a pet is very comforting."
            )
        if mode["key"] == "smell" and hometown:
            extra_parts.append(
                f"They grew up in {hometown} — a familiar home smell is lovely."
            )
        if mobility_level == "seated":
            extra_parts.append(
                "Keep the suggestion seated and gentle — no standing needed."
            )
        extra_str = " ".join(extra_parts)

        try:
            prompt = (
                f"Suggest one simple sensory activity for {name} using the "
                f"sense of {mode['key']}. "
                f"{mode['prompt_hint']} "
                f"{extra_str} "
                f"Keep it to 1 short sentence. Be specific and gentle. "
                f"Avoid anything potentially overwhelming or overstimulating. "
                f"Ensure the activity is accessible for someone who may be seated."
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
                return {"sensory": llm_response.content}
        except Exception as e:
            app_logger.error(f"LLM Error (sensory): {e}")

        suggestions = cfg.get(
            "suggestions",
            [
                "Today's suggested activity: Have a warm cup of tea "
                "and listen to {singer}."
            ],
        )
        selected = random.choice(suggestions)
        return {"sensory": selected.format(singer=singer)}
