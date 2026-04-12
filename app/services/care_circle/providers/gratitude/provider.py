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


GRATITUDE_MODES = [
    {
        "key": "nature",
        "instruction": (
            "Focus on something beautiful in nature — sunlight, a bird, "
            "a breeze, the smell of rain, or blooming flowers."
        ),
    },
    {
        "key": "person",
        "instruction": (
            "Focus on a person who brings warmth — a family member, "
            "an old friend, or a kind neighbour they remember fondly."
        ),
    },
    {
        "key": "simple_comfort",
        "instruction": (
            "Focus on a simple everyday comfort — a warm cup of tea, "
            "a cozy chair, a favourite song, or a soft blanket."
        ),
    },
    {
        "key": "memory",
        "instruction": (
            "Focus on a happy memory — a holiday, a childhood moment, "
            "a celebration, or a place they loved to visit."
        ),
    },
    {
        "key": "body",
        "instruction": (
            "Focus on something their body can do — taking a deep breath, "
            "feeling the warmth of the sun, or hearing music clearly."
        ),
    },
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

        mode = random.choice(GRATITUDE_MODES)

        try:
            prompt = (
                f"Write one gentle gratitude thought for {name}. "
                f"{mode['instruction']} "
                f"Keep it to 1-2 short sentences. "
                f"Do NOT ask a question that tests memory. "
                f"Do not mention illness, health problems, or care situations. "
                f"Keep the tone positive, warm, and uplifting."
            )
            llm_response = await generate_text_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT, max_tokens=256
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if llm_response.content and len(llm_response.content) > 10:
                return llm_response.content
        except Exception as e:
            app_logger.error(f"LLM Error (gratitude): {e}")

        prompts = cfg.get(
            "prompts", ["What is one thing that made you smile yesterday?"]
        )
        return random.choice(prompts)
