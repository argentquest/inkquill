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


GRATITUDE_MODES = [
    {"key": "nature", "instruction": "Focus on something beautiful in nature — sunlight, a bird, a breeze, the smell of rain, or blooming flowers."},
    {"key": "person", "instruction": "Focus on a person who brings warmth — a family member, an old friend, or a kind neighbour they remember fondly."},
    {"key": "simple_comfort", "instruction": "Focus on a simple everyday comfort — a warm cup of tea, a cozy chair, a favourite song, or a soft blanket."},
    {"key": "memory", "instruction": "Focus on a happy memory — a holiday, a childhood moment, a celebration, or a place they loved to visit."},
    {"key": "body", "instruction": "Focus on something their body can do — taking a deep breath, feeling the warmth of the sun, or hearing music clearly."},
    {"key": "food", "instruction": "Focus on a favourite food or meal they enjoy — the taste, the smell, or a warm memory of sharing it with someone."},
    {"key": "home", "instruction": "Focus on something about home that brings comfort — a familiar room, a cozy corner, or the sounds of a peaceful household."},
    {"key": "season", "instruction": "Focus on something beautiful about the current season — the colours outside, the weather, or how the air feels today."},
    {"key": "music", "instruction": "Focus on music they love — a song that always lifts their mood, a melody that brings back a smile, or the joy of singing."},
    {"key": "kindness", "instruction": "Focus on an act of kindness they have given or received — a helping hand, a warm word, or a small gesture of care."},
    {"key": "laughter", "instruction": "Focus on something that makes them laugh or smile — a funny story, a pet's behaviour, or a happy moment shared with others."},
    {"key": "achievement", "instruction": "Focus on something they are proud of — a skill, a role they played in life, or something they created or accomplished."},
    {"key": "senses", "instruction": "Focus on a pleasant sensory experience — a lovely scent, the feel of warm sunshine, or the sound of birds in the morning."},
    {"key": "friendship", "instruction": "Focus on a friendship that has meant a great deal — someone who has been kind, loyal, or fun to be around."},
    {"key": "peace", "instruction": "Focus on a moment or place of peace — a quiet garden, a favourite chair, a walk in the park, or a calm morning."},
]


class GratitudeProvider(BaseCareCircleProvider):
    provider_key = "gratitude"
    is_safe_for_patient = True

    """
    Generates a gentle thought of gratitude using a Large Language Model.

    Rotates across five gratitude themes (nature, person, simple comfort,
    memory, body) to keep daily reflections fresh and varied.
    """

    async def get_content(self, **kwargs) -> str:
        patient_profile = kwargs.get("patient_profile")
        cfg = self.patient_config
        name = getattr(patient_profile, "display_name", "friend") if patient_profile else "friend"

        patient_id = getattr(patient_profile, "id", None) if patient_profile else None
        mode = pick_avoiding_recent(
            GRATITUDE_MODES,
            "gratitude_mode",
            patient_id=patient_id,
            key_fn=lambda x: x["key"],
        )

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
                f"Write one gentle gratitude thought for {name}. "
                f"{mode['instruction']} "
                f"Keep it to 1-2 short sentences. "
                f"Do NOT ask a question that tests memory. "
                f"Do not mention illness, health problems, or care situations. "
                f"Keep the tone positive, warm, and uplifting."
            )
            llm_response = await generate_text_with_usage(
                prompt, system=self.get_system_prompt(patient_profile)
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=self.get_system_prompt(patient_profile),
            )
            if llm_response.content and len(llm_response.content) > 10:
                return llm_response.content
        except Exception as e:
            app_logger.error(f"LLM Error (gratitude): {e}")

        prompts = cfg.get(
            "prompts", ["What is one thing that made you smile yesterday?"]
        )
        return pick_avoiding_recent(prompts, "gratitude_fallback", patient_id=patient_id)
