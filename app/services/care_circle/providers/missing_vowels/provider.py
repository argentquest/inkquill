import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class MissingVowelsProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Missing Vowels Puzzle - Recognition-based word puzzle.

    Strips vowels (A, E, I, O, U) from familiar words, letting the brain
    fill in the shapes. This taps into recognition memory rather than recall,
    making it accessible for dementia care.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Generate a personalized 'Missing Vowels' puzzle.

        Constructs a word pool from the user's family members and favorite 
        activities, falling back to static default words. Strips vowels 
        from a selected word.

        Returns:
            dict: Containing puzzle 'type', 'title', 'instruction', the 
                  blanked 'puzzle' string, the 'answer', and a length 'hint'.
        """
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})

        # Build personalized word pool from profile + defaults
        word_pool = []

        # Add family member names (very familiar)
        family = prefs.get("family_members", [])
        word_pool.extend([name.upper() for name in family if len(name) >= 4])

        # Add words from hobbies/activities
        activities = prefs.get("favorite_activities", [])
        for activity in activities:
            words = activity.upper().split()
            word_pool.extend([w for w in words if len(w) >= 4])

        # Add engineering/Quebec-themed defaults from config
        default_words = cfg.get("words", [
            "TURBINE", "CONCRETE", "RESERVOIR", "QUEBEC", "MONTREAL",
            "BRIDGE", "ENGINEER", "RIVER", "FOREST", "WINTER",
            "GARDEN", "KITCHEN", "FAMILY", "SUNSHINE", "MORNING"
        ])
        word_pool.extend(default_words)

        # Filter to good puzzle words (4-10 letters, has vowels)
        vowels = "AEIOU"
        valid_words = [
            w for w in word_pool
            if 4 <= len(w) <= 10 and any(c in vowels for c in w)
        ]

        if not valid_words:
            valid_words = default_words

        word = random.choice(valid_words)
        puzzle_word = " ".join(
            ["_" if letter in vowels else letter for letter in word]
        )

        return {
            "type": "missing_vowels",
            "title": "Fill in the Vowels",
            "instruction": "The vowels (A, E, I, O, U) are missing. "
                           "Can you guess the word?",
            "puzzle": puzzle_word,
            "answer": word,
            "hint": f"It has {len(word)} letters"
        }
