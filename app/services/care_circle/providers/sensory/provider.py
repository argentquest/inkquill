import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    get_dementia_system_prompt,
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from app.services.care_circle.variety_utils import pick_avoiding_recent
from typing import Any, Dict


SENSORY_MODES = [
    {"key": "hearing_music", "sense": "hearing", "prompt_hint": "Suggest a piece of music or a favourite song to listen to that brings warmth and joy."},
    {"key": "hearing_nature", "sense": "hearing", "prompt_hint": "Suggest something peaceful to listen to in nature — birdsong, rain on the window, or wind through the trees."},
    {"key": "touch_warmth", "sense": "touch", "prompt_hint": "Suggest something warm and comforting to hold or feel — a hot water bottle, a warm cup, or sunshine on the skin."},
    {"key": "touch_soft", "sense": "touch", "prompt_hint": "Suggest something soft and soothing to touch — a cozy blanket, a pet's fur, or a favourite soft garment."},
    {"key": "smell_food", "sense": "smell", "prompt_hint": "Suggest a pleasant food smell to enjoy — fresh bread baking, coffee brewing, or a favourite meal cooking."},
    {"key": "smell_nature", "sense": "smell", "prompt_hint": "Suggest a lovely natural scent to seek out — flowers from the garden, fresh air, or the smell after rain."},
    {"key": "taste_warm", "sense": "taste", "prompt_hint": "Suggest a warm drink or comforting food to savour — a cup of tea, hot chocolate, or a favourite biscuit."},
    {"key": "taste_sweet", "sense": "taste", "prompt_hint": "Suggest something sweet and enjoyable to taste — a piece of fruit, a small treat, or a favourite snack."},
    {"key": "sight_beauty", "sense": "sight", "prompt_hint": "Suggest something beautiful to look at — a view from the window, colourful flowers, or a favourite photograph."},
    {"key": "sight_calming", "sense": "sight", "prompt_hint": "Suggest something calming to watch — a candle flame, clouds moving, leaves in the breeze, or birds in the garden."},
    {"key": "movement_gentle", "sense": "touch", "prompt_hint": "Suggest a very gentle movement to enjoy — slowly stretching fingers, feeling the ground under their feet, or a slow breath."},
    {"key": "hearing_voice", "sense": "hearing", "prompt_hint": "Suggest listening to a familiar, comforting voice — a loved one reading aloud, a favourite presenter, or a recorded message."},
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
        patient_id_for_singer = getattr(patient_profile, "id", None) if patient_profile else None
        singer = pick_avoiding_recent(singers, "sensory_singer", patient_id=patient_id_for_singer) if singers else default_singer

        favourite_foods = prefs.get("favourite_foods", [])
        pets = prefs.get("pets", [])
        hometown = prefs.get("hometown", "")
        mobility_level = prefs.get("mobility_level", "")

        patient_id = getattr(patient_profile, "id", None) if patient_profile else None
        mode = pick_avoiding_recent(
            SENSORY_MODES,
            "sensory_mode",
            patient_id=patient_id,
            key_fn=lambda x: x["key"],
        )
        sense = mode.get("sense", mode["key"])

        # Build sense-specific personal context
        import random as _rnd
        extra_parts = []
        if sense == "hearing":
            extra_parts.append(f"They enjoy music by {singer}.")
        if sense == "taste" and favourite_foods:
            extra_parts.append(f"A food they love is {_rnd.choice(favourite_foods)}.")
        if sense == "touch" and pets:
            extra_parts.append(f"They have {pets[0]} — stroking a pet is very comforting.")
        if sense == "smell" and hometown:
            extra_parts.append(f"They grew up in {hometown} — a familiar home smell is lovely.")
        if mobility_level == "seated":
            extra_parts.append(
                "Keep the suggestion seated and gentle — no standing needed."
            )
        extra_str = " ".join(extra_parts)

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
                f"Suggest one simple sensory activity for {name} using the "
                f"sense of {sense}. "
                f"{mode['prompt_hint']} "
                f"{extra_str} "
                f"Keep it to 1 short sentence. Be specific and gentle. "
                f"Avoid anything potentially overwhelming or overstimulating. "
                f"Ensure the activity is accessible for someone who may be seated."
            )
            llm_response = await generate_text_with_usage(
                prompt, system=get_dementia_system_prompt(self.get_generation_date())
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=get_dementia_system_prompt(self.get_generation_date()),
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
        selected = pick_avoiding_recent(suggestions, "sensory_fallback")
        return {"sensory": selected.format(singer=singer)}
