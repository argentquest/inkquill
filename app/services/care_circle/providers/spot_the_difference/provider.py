"""
Spot the Difference (Text Version) provider.

Two lists of 5 familiar words — identical except one item is swapped.
The reader identifies which word changed between List A and List B.
LLM generates the lists; falls back to static pairs from config.
"""

import random

import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict



class SpotTheDifferenceProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    Spot the Difference — two near-identical word lists.

    Uses LLM to generate fresh pairs daily. Falls back to a static
    set from config.json if the LLM call fails.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config

        try:
            prompt = (
                "Create a simple 'Spot the Difference' word puzzle for an elderly person.\n"
                "Write two lists (List A and List B), each with exactly 5 short, familiar words.\n"
                "The lists must be identical EXCEPT one word is different between them.\n"
                "Use only simple, familiar words: animals, food, colours, flowers, household items.\n"
                "Return ONLY valid JSON in this exact format:\n"
                '{"list_a": ["Word1","Word2","Word3","Word4","Word5"], '
                '"list_b": ["Word1","Word2","Word3","Word4","Word5"], '
                '"changed_in_a": "original word", "changed_in_b": "replacement word"}'
            )
            data, llm_resp = await generate_json_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(llm_resp)

            list_a = data.get("list_a", [])
            list_b = data.get("list_b", [])
            changed_a = data.get("changed_in_a", "")
            changed_b = data.get("changed_in_b", "")

            if (
                len(list_a) == 5
                and len(list_b) == 5
                and changed_a
                and changed_b
            ):
                return {
                    "title": "Spot the Difference",
                    "instruction": (
                        "One word has changed between List A and List B. "
                        "Can you find it?"
                    ),
                    "list_a": [w.capitalize() for w in list_a],
                    "list_b": [w.capitalize() for w in list_b],
                    "changed_in_a": changed_a.capitalize(),
                    "changed_in_b": changed_b.capitalize(),
                }
        except Exception as e:
            app_logger.error(f"LLM Error (spot_the_difference): {e}")

        # Fallback: pick a static word set
        fallback_sets = cfg.get("fallback_sets", [])
        chosen = random.choice(fallback_sets)
        return {
            "title": "Spot the Difference",
            "instruction": (
                "One word has changed between List A and List B. "
                "Can you find it?"
            ),
            "list_a": chosen["list_a"],
            "list_b": chosen["list_b"],
            "changed_in_a": chosen["changed_in_a"],
            "changed_in_b": chosen["changed_in_b"],
        }
