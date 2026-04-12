import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class MissingVowelsProvider(BaseCareCircleProvider):
    provider_key = "missing_vowels"
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
        from a selected word. Difficulty config controls word length and hints.

        Returns:
            dict: Containing puzzle 'type', 'title', 'instruction', the
                  blanked 'puzzle' string, the 'answer', and a length 'hint'.
        """
        cfg = self.patient_config
        diff_config = self.difficulty_config
        prefs = self.get_patient_preferences(patient_profile)

        # Get difficulty-based word length constraints
        min_length = diff_config.get("min_word_length", 4)
        max_length = diff_config.get("max_word_length", 10)
        show_vowel_count = diff_config.get("show_vowel_count", True)
        show_consonants = diff_config.get("show_consonants", True)

        # Build personalized word pool from profile + defaults
        word_pool = []

        # Add family member names (very familiar)
        family = prefs.get("family_members", [])
        word_pool.extend([name.upper() for name in family if len(name) >= min_length])

        # Add words from hobbies/activities
        activities = prefs.get("favorite_activities", [])
        for activity in activities:
            words = activity.upper().split()
            word_pool.extend([w for w in words if len(w) >= min_length])

        # Add engineering/Quebec-themed defaults from config
        default_words = cfg.get("words", [
            "TURBINE", "CONCRETE", "RESERVOIR", "QUEBEC", "MONTREAL",
            "BRIDGE", "ENGINEER", "RIVER", "FOREST", "WINTER",
            "GARDEN", "KITCHEN", "FAMILY", "SUNSHINE", "MORNING"
        ])
        word_pool.extend(default_words)

        # Filter to good puzzle words based on difficulty length constraints
        vowels = "AEIOU"
        valid_words = [
            w for w in word_pool
            if min_length <= len(w) <= max_length and any(c in vowels for c in w)
        ]

        if not valid_words:
            valid_words = [w for w in default_words if min_length <= len(w) <= max_length]
        if not valid_words:
            valid_words = default_words

        word = random.choice(valid_words)

        # Build puzzle display based on difficulty settings
        if show_consonants:
            puzzle_word = " ".join(
                ["_" if letter in vowels else letter for letter in word]
            )
        else:
            puzzle_word = " ".join(["_" for letter in word])

        # Build hint based on difficulty
        hint_parts = [f"It has {len(word)} letters"]
        if show_vowel_count:
            vowel_count = sum(1 for c in word if c in vowels)
            hint_parts.append(f"{vowel_count} vowels missing")
        hint = ". ".join(hint_parts)

        return {
            "type": "missing_vowels",
            "title": "Fill in the Vowels",
            "instruction": "The vowels (A, E, I, O, U) are missing. "
                           "Can you guess the word?",
            "puzzle": puzzle_word,
            "answer": word,
            "hint": hint,
            "difficulty": self.difficulty_level,
            "show_vowel_count": show_vowel_count,
        }
