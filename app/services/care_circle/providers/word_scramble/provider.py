import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class WordScrambleProvider(BaseCareCircleProvider):
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
        any family member names.
        
        Returns:
            dict: The scramble puzzle properties including 'type', 'title', 
                  'instruction', the scrambled 'puzzle', the 'answer', and an 
                  initial letter 'hint'.
        """
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})

        # Short, highly familiar words (4-6 letters ideal)
        word_pool = list(cfg.get("words", [
            "WATER", "RIVER", "TREES", "BIRDS", "SNOW", "LAKE", "FISH",
            "DAM", "STEEL", "PIPE", "BOLT",
            "HOME", "BREAD", "CHAIR", "LIGHT", "WARM",
            "MAPLE", "FROST", "CABIN"
        ]))

        # Add family first names (short ones)
        family = prefs.get("family_members", [])
        for name in family:
            if 3 <= len(name) <= 6:
                word_pool.append(name.upper())

        word = random.choice(word_pool)

        # Safety net: keep first and last letters, scramble middle
        if len(word) <= 3:
            # For 3-letter words, just scramble all
            letters = list(word)
            random.shuffle(letters)
            scrambled = "".join(letters)
        else:
            # Keep first and last, scramble middle
            middle = list(word[1:-1])
            random.shuffle(middle)
            scrambled = word[0] + "".join(middle) + word[-1]

        # Make sure it's actually scrambled (not the same)
        attempts = 0
        while scrambled == word and attempts < 10:
            if len(word) <= 3:
                letters = list(word)
                random.shuffle(letters)
                scrambled = "".join(letters)
            else:
                middle = list(word[1:-1])
                random.shuffle(middle)
                scrambled = word[0] + "".join(middle) + word[-1]
            attempts += 1

        # Space out letters for readability
        display_scramble = " ".join(scrambled)

        return {
            "type": "word_scramble",
            "title": "Unscramble the Word",
            "instruction": "Rearrange these letters to make a word.",
            "puzzle": display_scramble,
            "answer": word,
            "hint": f"Hint: The first letter is {word[0]}" if len(word) > 3 else None
        }
