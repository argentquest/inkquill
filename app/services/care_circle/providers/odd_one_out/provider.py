import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class OddOneOutProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Odd One Out Logic Game - Categorization puzzle.

    Engages categorization skills without requiring writing - the user
    can just point to or circle the answer. Three items from one category
    plus one from a different category, shuffled randomly.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Assemble the 'odd one out' puzzle array.

        Randomly selects categories (customizing with family members 
        if applicable) and populates the decoy items along with the 
        single mismatching answer.

        Returns:
            dict: Puzzle configuration containing 'type', 'title', 
                  'instruction', the list of 'items', the 'answer', 
                  and an 'explanation'.
        """
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})

        # Categories tailored for civil engineer who loves outdoors
        categories = cfg.get("categories", {
            "tools": ["Hammer", "Wrench", "Screwdriver", "Level", "Pliers"],
            "weather": ["Snow", "Rain", "Sunshine", "Clouds", "Wind"],
        })

        # Add family names as a category if available
        family = prefs.get("family_members", [])
        if len(family) >= 3:
            categories["family"] = family

        # Pick two different categories
        category_names = list(categories.keys())
        if len(category_names) < 2:
            category_names = ["tools", "weather"]

        main_category = random.choice(category_names)
        other_categories = [c for c in category_names if c != main_category]
        odd_category = random.choice(other_categories)

        # Pick 3 from main category, 1 from odd category
        main_items = random.sample(
            categories[main_category],
            min(3, len(categories[main_category]))
        )
        odd_item = random.choice(categories[odd_category])

        puzzle_items = main_items + [odd_item]
        random.shuffle(puzzle_items)

        return {
            "type": "odd_one_out",
            "title": "Which One Doesn't Belong?",
            "instruction": "Circle the word that doesn't fit with the others.",
            "items": puzzle_items,
            "answer": odd_item,
            "explanation": f"The others are all {main_category}"
        }
