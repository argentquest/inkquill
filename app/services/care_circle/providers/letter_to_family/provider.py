"""
Letter to Family provider for Care Circle patient sessions.
Uses an LLM to generate a warm, short letter that the patient could imagine
sending or sharing with their family — a conversation starter and connection builder.
Falls back to a curated static pool if LLM is unavailable.
"""

import random
import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_json_with_usage,
)

logger = logging.getLogger(__name__)


LETTER_THEMES = [
    "a favourite memory from your childhood",
    "the best holiday or trip you ever took",
    "your favourite season and what you love about it",
    "a meal you remember cooking or eating that made you very happy",
    "something you are grateful for today",
    "a funny or happy moment from long ago that still makes you smile",
    "a hobby or activity you have always loved",
    "something beautiful you noticed recently — in nature or around you",
    "a piece of advice you would share with someone you love",
    "something you are looking forward to",
]

FALLBACK_LETTERS = [
    {
        "greeting": "Dear Family,",
        "body": (
            "I have been thinking about you all today and wanted to share a little note. "
            "I was remembering how we used to sit together at the kitchen table on Sunday mornings — "
            "the smell of toast, the sound of laughter, everyone talking at once. "
            "Those are some of my most treasured memories. "
            "I hope you know how much those moments mean to me. "
            "Sending all my love to each and every one of you."
        ),
        "signature": "With love and warm wishes",
    },
    {
        "greeting": "My Dearest Ones,",
        "body": (
            "I am so grateful for beautiful days like today. "
            "I looked out the window this morning and the garden looked just lovely — "
            "it reminded me of the flowers we used to grow together when you were small. "
            "I am so proud of each of you and think about you often. "
            "You bring so much joy to my life. "
            "Never forget how loved you are."
        ),
        "signature": "All my love, always",
    },
    {
        "greeting": "To My Wonderful Family,",
        "body": (
            "I have been thinking about all the wonderful adventures we have shared together over the years — "
            "the trips, the celebrations, the quiet evenings, and the silly moments that made us all laugh. "
            "Every single memory is a treasure I hold close to my heart. "
            "Thank you for filling my life with so much warmth and happiness. "
            "I am the luckiest person in the world to have a family like you."
        ),
        "signature": "Forever yours",
    },
    {
        "greeting": "Hello My Loves,",
        "body": (
            "Today I am thinking about the small things that make life so beautiful — "
            "a good cup of tea, a favourite song on the radio, the sound of rain on the window. "
            "These simple joys remind me that happiness is all around us if we slow down to notice. "
            "I hope your day is full of little moments like these. "
            "You are always in my thoughts and in my heart."
        ),
        "signature": "With all the love in the world",
    },
    {
        "greeting": "Dear Family,",
        "body": (
            "I wanted to share something I have been thinking about lately. "
            "If I could give one piece of advice, it would be this: "
            "take time to enjoy the people around you. "
            "The conversations over the dinner table, the long walks, the evenings playing games — "
            "those are the moments that matter most. "
            "I hope you are all making time for each other. "
            "Life is a gift, and so are you."
        ),
        "signature": "With so much love",
    },
]


class LetterToFamilyProvider(BaseCareCircleProvider):
    provider_key = "letter_to_family"
    is_safe_for_patient = True

    """
    Generates a warm short letter from the patient's point of view using an LLM.
    Themed around happy memories, gratitude, and connection.
    Falls back to 5 curated static letters if LLM is unavailable.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        patient_name = getattr(patient_profile, "display_name", "Friend")
        theme = random.choice(LETTER_THEMES)

        try:
            prompt = (
                f"Write a short, warm letter from an elderly person named {patient_name} to their family. "
                f"The letter should be about: {theme}. "
                f"Keep it to 3-4 sentences. Use a loving, gentle, and personal tone. "
                f"The letter should feel heartfelt and real — like something you would actually write to people you love. "
                f"Do not use any distressing, sad, or negative content. "
                f"Return as JSON: "
                '{"greeting": "Dear Family,", "body": "...", "signature": "With love"}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT, max_tokens=256
            )
            self.log_llm_response(llm_response, prompt=prompt, system_prompt=DEMENTIA_SYSTEM_PROMPT)
            if data.get("greeting") and data.get("body"):
                return data
        except Exception as e:
            logger.error(f"LLM Error (letter_to_family): {e}")

        fallback_pool = cfg.get("letters", FALLBACK_LETTERS)
        return random.choice(fallback_pool)
