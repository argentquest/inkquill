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


QUESTION_TYPES = [
    {
        "key": "phrase",
        "label": "A familiar saying to finish",
        "example": "like 'An apple a day keeps the...'",
        "has_answer": True,
    },
    {
        "key": "either_or",
        "label": "A simple 'which do you prefer?' question",
        "example": "like 'Cake or pie?'",
        "has_answer": False,
    },
    {
        "key": "name_three",
        "label": "A 'can you name three...' prompt",
        "example": "like 'Can you name three flowers?'",
        "has_answer": False,
    },
    {
        "key": "true_false",
        "label": "A gentle true or false question",
        "example": "like 'True or false: The sun rises in the east.'",
        "has_answer": True,
    },
]


class BrainBoosterProvider(BaseCareCircleProvider):
    provider_key = "brain_booster"
    is_safe_for_patient = True

    """
    Generates gentle cognitive exercises using a Large Language Model.

    Rotates across four question types — phrase completion, either/or,
    name three, and true/false — to keep content fresh day to day.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        era = prefs.get("era_of_youth", "1950s")

        qt = random.choice(QUESTION_TYPES)
        answer_field = (
            '"answer": "the correct answer"'
            if qt["has_answer"]
            else '"answer": ""'
        )

        try:
            prompt = (
                f"Create one fun, gentle thinking activity for someone "
                f"who grew up in the {era}. "
                f"Use this type: {qt['label']} ({qt['example']}). "
                f"The activity must feel easy and fun, never like a test. "
                f"Avoid topics that could trigger negative or distressing memories. "
                f"Use only common knowledge that most people would recognize. "
                f"Return as JSON: "
                f'{{"type": "{qt["key"]}", "prompt": "...", {answer_field}}}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if data.get("prompt"):
                return data
        except Exception as e:
            app_logger.error(f"LLM Error (brain_booster): {e}")

        prompts = cfg.get("prompts", [])
        matching = [p for p in prompts if p.get("type") == qt["key"]]
        pool = matching if matching else prompts
        return (
            random.choice(pool)
            if pool
            else {"type": "either_or", "prompt": "Coffee or tea?", "answer": ""}
        )
