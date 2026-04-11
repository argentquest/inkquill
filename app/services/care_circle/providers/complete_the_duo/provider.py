"""
Complete the Duo provider.

Shows one half of a well-known pair and asks the reader to complete it.
Pure recognition — almost impossible to get wrong. No LLM required.
Pairs are selected daily via a stable date-hash so all profiles see
the same set each day.
"""

import datetime
import hashlib
import random

import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class CompleteTheDuoProvider(BaseCareCircleProvider):
    provider_key = "complete_the_duo"
    is_safe_for_patient = True

    """
    Complete the Duo — famous pairs puzzle.

    Picks N pairs per day from a static config bank, seeded by today's
    date so the selection is consistent throughout the day.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        pairs = cfg.get("pairs", [])
        pairs_per_day = cfg.get("pairs_per_day", 4)

        # Stable daily selection — same pairs for all profiles today
        today = datetime.date.today().isoformat()
        seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        selected = rng.sample(pairs, min(pairs_per_day, len(pairs)))

        return {
            "title": "Complete the Duo!",
            "instruction": "Can you fill in the missing half?",
            "pairs": [
                {"prompt": p["prompt"], "answer": p["answer"]}
                for p in selected
            ],
        }
