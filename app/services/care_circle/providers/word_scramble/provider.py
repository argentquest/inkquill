import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class WordScrambleProvider(BaseCareCircleProvider):
    provider_key = "word_scramble"
    is_safe_for_patient = True

    """
    Word Scramble Puzzle - With safety net.

    Standard anagrams can be frustrating if words are too long. This version
    keeps words to 4-6 letters max, and leaves the first and last letters in
    their correct places to provide a helpful anchor.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Assemble the bounded anagram puzzle.
        
        Collects suitable short words from the general pool along with
        any family member names. Difficulty config controls word length
        and hint availability.
        
        Returns:
            dict: The scramble puzzle properties including 'type', 'title',
                  'instruction', the scrambled 'puzzle', the 'answer', and an
                  initial letter 'hint'.
        """
        cfg = self.patient_config
        diff_config = self.difficulty_config
        prefs = self.get_patient_preferences(patient_profile)

        # Get difficulty-based settings
        min_length = diff_config.get("min_word_length", 4)
        max_length = diff_config.get("max_word_length", 6)
        hint_available = diff_config.get("hint_available", True)
        show_first_letter = diff_config.get("show_first_letter", True)

        # Filter word pool by difficulty length constraints
        all_words = cfg.get("words", [
            "WATER", "RIVER", "TREES", "BIRDS", "SNOW", "LAKE", "FISH",
            "DAM", "STEEL", "PIPE", "BOLT",
            "HOME", "BREAD", "CHAIR", "LIGHT", "WARM",
            "MAPLE", "FROST", "CABIN"
        ])
        word_pool = [w for w in all_words if min_length <= len(w) <= max_length]

        # Add family first names (within length constraints)
        family = prefs.get("family_members", [])
        for name in family:
            upper_name = name.upper()
            if min_length <= len(upper_name) <= max_length:
                word_pool.append(upper_name)

        if not word_pool:
            word_pool = [w for w in all_words if min_length <= len(w) <= max_length]
        if not word_pool:
            word_pool = all_words

        word = random.choice(word_pool)

        # Scramble strategy varies by difficulty
        if show_first_letter and len(word) > 2:
            # Keep first letter, scramble rest
            middle = list(word[1:])
            random.shuffle(middle)
            scrambled = word[0] + "".join(middle)
        elif len(word) > 3:
            # Keep first and last, scramble middle
            middle = list(word[1:-1])
            random.shuffle(middle)
            scrambled = word[0] + "".join(middle) + word[-1]
        else:
            # Full scramble
            letters = list(word)
            random.shuffle(letters)
            scrambled = "".join(letters)

        # Make sure it's actually scrambled (not the same)
        attempts = 0
        while scrambled == word and attempts < 10:
            letters = list(word)
            random.shuffle(letters)
            scrambled = "".join(letters)
            attempts += 1

        # Space out letters for readability
        display_scramble = " ".join(scrambled)

        # Build hint based on difficulty
        hint = None
        if hint_available:
            if show_first_letter:
                hint = f"First letter: {word[0]}"
            else:
                hint = f"{len(word)} letters"

        return {
            "type": "word_scramble",
            "title": "Unscramble the Word",
            "instruction": "Rearrange these letters to make a word.",
            "puzzle": display_scramble,
            "answer": word,
            "hint": hint,
            "difficulty": self.difficulty_level,
            "show_first_letter": show_first_letter,
        }
