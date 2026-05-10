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
    {
        "key": "rhyme",
        "label": "A simple rhyming word to complete",
        "example": "like 'Jack and Jill went up the ___'",
        "has_answer": True,
    },
    {
        "key": "category",
        "label": "Name something that belongs to a familiar category",
        "example": "like 'Name a fruit that starts with A'",
        "has_answer": False,
    },
    {
        "key": "opposite",
        "label": "A gentle 'what is the opposite of?' question",
        "example": "like 'What is the opposite of hot?'",
        "has_answer": True,
    },
    {
        "key": "colour",
        "label": "A colour-association question",
        "example": "like 'What colour is a ripe banana?'",
        "has_answer": True,
    },
    {
        "key": "number",
        "label": "A simple counting or number question",
        "example": "like 'How many days are in a week?'",
        "has_answer": True,
    },
    {
        "key": "season",
        "label": "A question about seasons or weather",
        "example": "like 'Which season comes after summer?'",
        "has_answer": True,
    },
    {
        "key": "animal",
        "label": "A gentle animal-knowledge question",
        "example": "like 'What sound does a cow make?'",
        "has_answer": True,
    },
    {
        "key": "memory",
        "label": "A pleasant 'do you remember?' question with no wrong answer",
        "example": "like 'Do you remember your favourite childhood meal?'",
        "has_answer": False,
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
        prefs = self.get_patient_preferences(patient_profile)
        era = prefs.get("era_of_youth", "1950s")

        qt = pick_avoiding_recent(
            QUESTION_TYPES,
            "brain_booster_type",
            key_fn=lambda x: x["key"],
        )
        answer_field = (
            '"answer": "the correct answer"'
            if qt["has_answer"]
            else '"answer": ""'
        )

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
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
                prompt, system=self.get_system_prompt(patient_profile)
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=self.get_system_prompt(patient_profile),
            )
            if data.get("prompt"):
                return data
        except Exception as e:
            app_logger.error(f"LLM Error (brain_booster): {e}")

        prompts = cfg.get("prompts", [])
        matching = [p for p in prompts if p.get("type") == qt["key"]]
        pool = matching if matching else prompts
        return (
            pick_avoiding_recent(pool, "brain_booster_fallback", key_fn=lambda x: x.get("prompt", str(x)))
            if pool
            else {"type": "either_or", "prompt": "Coffee or tea?", "answer": ""}
        )
