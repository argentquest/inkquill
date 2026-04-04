import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class FinishPhraseProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    Finish the Phrase Puzzle - Idioms & Lyrics completion.

    Phrases are era-tagged so the selection is weighted toward the
    user's generation, with universal idioms always available as fallback.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        era = prefs.get("era_of_youth", "")

        all_phrases = cfg.get("phrases", [])

        if era:
            era_phrases = [
                p for p in all_phrases
                if p.get("era") in (era, "all")
            ]
        else:
            era_phrases = all_phrases

        pool = era_phrases if era_phrases else all_phrases
        selected = random.choice(pool)

        result = {
            "type": "finish_phrase",
            "title": "Finish the Phrase",
            "instruction": "Can you complete this familiar saying?",
            "phrase": selected["phrase"] + " ________",
            "answer": selected["answer"],
            "category": selected.get("category", "idiom"),
        }

        if selected.get("artist"):
            result["hint"] = f"From a song by {selected['artist']}"

        return result
