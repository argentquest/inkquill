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


RIDDLE_STYLES = [
    {
        "key": "what_am_i",
        "instruction": (
            "Write a 'What am I?' riddle. "
            "Describe the object in one sentence and ask 'What am I?' at the end."
        ),
        "example": "I have a face but no eyes, hands but no fingers. What am I? (A clock)",
    },
    {
        "key": "finish_me",
        "instruction": (
            "Write a riddle as a short rhyme of two lines where the last word is missing. "
            "Example: 'I bark but I'm not a tree, I wag but I'm not a flag — I am a ___' "
            "Leave the answer blank and include it separately."
        ),
        "example": "A two-line rhyme riddle",
    },
    {
        "key": "knock_knock",
        "instruction": (
            "Write a gentle, funny knock-knock joke. "
            "Format: Knock knock / Who's there / [word] / [word] who / [punchline]."
        ),
        "example": "Knock knock... who's there... Lettuce... Lettuce who? Lettuce in, it's cold!",
    },
    {
        "key": "animal_riddle",
        "instruction": (
            "Write a riddle where the answer is a common friendly animal. "
            "Give two clues about the animal without naming it."
        ),
        "example": "I have four legs and say moo. What am I? (A cow)",
    },
    {
        "key": "household_object",
        "instruction": (
            "Write a riddle where the answer is a common household object. "
            "Describe what it does in one fun sentence."
        ),
        "example": "I hold your clothes but have no arms. What am I? (A wardrobe)",
    },
]


class RiddleProvider(BaseCareCircleProvider):
    provider_key = "riddle"
    is_safe_for_patient = True

    """
    Generates simple, easy-to-guess riddles using a Large Language Model.

    Rotates across five riddle styles — what am I, rhyme finish, knock-knock,
    animal, and household object — for daily variety.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config

        style = random.choice(RIDDLE_STYLES)

        try:
            prompt = (
                f"{style['instruction']} "
                f"The riddle must feel fun and easy — never frustrating. "
                f"Use only common, well-known objects or animals — avoid obscure vocabulary. "
                f"The answer must be something almost everyone would recognize. "
                f"Example style: {style['example']}. "
                'Return as JSON: {"question": "...", "answer": "..."}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT, max_tokens=128
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if data.get("question") and data.get("answer"):
                return data
        except Exception as e:
            app_logger.error(f"LLM Error (riddle): {e}")

        riddles = cfg.get(
            "riddles",
            [{"question": "What has hands but can't clap?", "answer": "A clock"}],
        )
        return random.choice(riddles)
