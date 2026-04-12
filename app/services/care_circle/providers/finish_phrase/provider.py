import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class FinishPhraseProvider(BaseCareCircleProvider):
    provider_key = "finish_phrase"
    is_safe_for_patient = True

    """
    Finish the Phrase Puzzle - Idioms & Lyrics completion.

    Phrases are era-tagged so the selection is weighted toward the
    user's generation, with universal idioms always available as fallback.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        diff_config = self.difficulty_config
        prefs = self.get_patient_preferences(patient_profile)
        era = prefs.get("era_of_youth", "")

        # Get difficulty-based settings
        allowed_categories = diff_config.get("categories", ["idiom", "lyric"])
        hint_available = diff_config.get("hint_available", True)
        show_first_letter = diff_config.get("show_first_letter", True)

        all_phrases = cfg.get("phrases", [])

        # Filter by era and allowed categories
        if era:
            era_phrases = [
                p for p in all_phrases
                if p.get("era") in (era, "all") and p.get("category") in allowed_categories
            ]
        else:
            era_phrases = [
                p for p in all_phrases
                if p.get("category") in allowed_categories
            ]

        pool = era_phrases if era_phrases else [
            p for p in all_phrases if p.get("category") in allowed_categories
        ]
        if not pool:
            pool = all_phrases

        selected = random.choice(pool)

        result = {
            "type": "finish_phrase",
            "title": "Finish the Phrase",
            "instruction": "Can you complete this familiar saying?",
            "phrase": selected["phrase"] + " ________",
            "answer": selected["answer"],
            "category": selected.get("category", "idiom"),
            "difficulty": self.difficulty_level,
        }

        # Build hint based on difficulty
        if hint_available:
            if selected.get("artist"):
                result["hint"] = f"From a song by {selected['artist']}"
            elif show_first_letter:
                result["hint"] = f"Starts with: {selected['answer'][0]}"

        return result
