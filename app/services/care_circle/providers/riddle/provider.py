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
    {
        "key": "food_riddle",
        "instruction": (
            "Write a riddle where the answer is a common food or drink. "
            "Give a fun clue about its colour, taste, or use."
        ),
        "example": "I'm yellow and curvy, monkeys love me. What am I? (A banana)",
    },
    {
        "key": "nature_riddle",
        "instruction": (
            "Write a riddle where the answer is something found in nature — "
            "a tree, a flower, a weather event, or a season. "
            "Describe it warmly in one sentence."
        ),
        "example": "I fall from the sky in winter and no two of me are alike. What am I? (A snowflake)",
    },
    {
        "key": "garden_riddle",
        "instruction": (
            "Write a riddle where the answer is a garden creature or plant. "
            "Keep it cheerful and easy to guess."
        ),
        "example": "I have petals and no feet, but I stand up tall. What am I? (A flower)",
    },
    {
        "key": "two_truths",
        "instruction": (
            "Write a riddle that gives three clues about a familiar everyday object, "
            "person, or creature. Ask 'What am I?' at the end. Make all three clues simple."
        ),
        "example": "I tick, I tock, I hang on the wall. What am I? (A clock)",
    },
    {
        "key": "fill_in_the_blank",
        "instruction": (
            "Write a gentle fill-in-the-blank sentence about everyday life. "
            "Leave one familiar word blank for the reader to supply."
        ),
        "example": "Every morning I put the kettle on to make a cup of ___. (Tea)",
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
        diff_config = self.difficulty_config
        difficulty = self.difficulty_level

        # Filter riddle styles based on difficulty type preference
        difficulty_type = diff_config.get("type", "object")
        if difficulty_type == "object":
            allowed_styles = ["what_am_i", "animal_riddle", "household_object"]
        elif difficulty_type == "mixed":
            allowed_styles = ["what_am_i", "finish_me", "animal_riddle", "household_object"]
        else:  # abstract
            allowed_styles = ["finish_me", "knock_knock"]

        applicable_styles = [s for s in RIDDLE_STYLES if s["key"] in allowed_styles]
        pool = applicable_styles if applicable_styles else RIDDLE_STYLES
        style = pick_avoiding_recent(pool, "riddle_style", key_fn=lambda x: x["key"])

        # Adjust prompt based on difficulty
        hint_text = ""
        if diff_config.get("hint_available", True):
            hint_text = (
                f"Include a gentle hint in the question if possible. "
                f"The riddle type is: {difficulty_type}."
            )

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
                f"{style['instruction']} "
                f"{hint_text} "
                f"The riddle must feel fun and {'easy' if difficulty == 'easy' else 'engaging'} — never frustrating. "
                f"Use only common, well-known objects or animals — avoid obscure vocabulary. "
                f"The answer must be something almost everyone would recognize. "
                f"Example style: {style['example']}. "
                'Return as JSON: {"question": "...", "answer": "..."}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=get_dementia_system_prompt(self.get_generation_date())
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=get_dementia_system_prompt(self.get_generation_date()),
            )
            if data.get("question") and data.get("answer"):
                # Add difficulty metadata to the response
                data["difficulty"] = difficulty
                data["hint_available"] = diff_config.get("hint_available", True)
                data["auto_reveal_answer"] = diff_config.get("auto_reveal_answer", False)
                return data
        except Exception as e:
            app_logger.error(f"LLM Error (riddle): {e}")

        riddles = cfg.get(
            "riddles",
            [
                {"question": "What has hands but can't clap?", "answer": "A clock"},
                {"question": "I bark but I'm not a dog, and I'm found in a forest. What am I?", "answer": "A tree"},
                {"question": "I'm round and yellow, and I shine every morning. What am I?", "answer": "The sun"},
                {"question": "I have a tail but no legs, and I live in water. What am I?", "answer": "A fish"},
                {"question": "I melt in your cup and keep you warm on a cold day. What am I?", "answer": "A hot drink"},
                {"question": "I have petals but no feet, and I smell lovely in spring. What am I?", "answer": "A flower"},
                {"question": "I have four legs and say moo. What am I?", "answer": "A cow"},
                {"question": "I'm filled with letters but I'm not a book — you find me at the door. What am I?", "answer": "A letter box"},
                {"question": "I have hands and numbers but I can't count. What am I?", "answer": "A clock"},
                {"question": "I grow in the garden and you eat me for lunch. I'm green and crunchy. What am I?", "answer": "A cucumber"},
                {"question": "I tweet and I sing but I'm not on a phone. I have feathers and wings. What am I?", "answer": "A bird"},
                {"question": "I'm made every morning and slept in every night. What am I?", "answer": "A bed"},
                {"question": "Every morning I put the kettle on to make a cup of ___.", "answer": "Tea"},
                {"question": "I bounce and I bounce, children love to play with me. What am I?", "answer": "A ball"},
                {"question": "I fall from the sky in winter and no two of me are alike. What am I?", "answer": "A snowflake"},
            ],
        )
        result = pick_avoiding_recent(riddles, "riddle_fallback", key_fn=lambda x: x["question"])
        result["difficulty"] = difficulty
        result["hint_available"] = diff_config.get("hint_available", True)
        result["auto_reveal_answer"] = diff_config.get("auto_reveal_answer", False)
        return result
