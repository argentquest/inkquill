import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class OddOneOutProvider(BaseCareCircleProvider):
    provider_key = "odd_one_out"
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
        single mismatching answer. Difficulty config controls category
        selection and hint availability.

        Returns:
            dict: Puzzle configuration containing 'type', 'title',
                  'instruction', the list of 'items', the 'answer',
                  and an 'explanation'.
        """
        cfg = self.patient_config
        diff_config = self.difficulty_config
        prefs = self.get_patient_preferences(patient_profile)

        # Get difficulty-based settings
        hint_available = diff_config.get("hint_available", True)
        show_explanation = diff_config.get("show_explanation", True)
        preferred_categories = diff_config.get("preferred_categories", [])

        # All available categories from config
        all_categories = cfg.get("categories", {
            "tools": ["Hammer", "Wrench", "Screwdriver", "Level", "Pliers"],
            "weather": ["Snow", "Rain", "Sunshine", "Clouds", "Wind"],
        })

        # Add family names as a category if available
        family = prefs.get("family_members", [])
        if len(family) >= 3:
            all_categories["family"] = family

        # Select category pool based on difficulty preferences
        if preferred_categories:
            available = [c for c in preferred_categories if c in all_categories]
            if not available:
                available = list(all_categories.keys())
        else:
            available = list(all_categories.keys())

        if len(available) < 2:
            available = list(all_categories.keys())[:2]

        # Pick two different categories
        main_category = random.choice(available)
        other_categories = [c for c in available if c != main_category]
        if not other_categories:
            other_categories = [c for c in all_categories.keys() if c != main_category]
        odd_category = random.choice(other_categories) if other_categories else main_category

        # Pick 3 from main category, 1 from odd category
        main_items = random.sample(
            all_categories[main_category],
            min(3, len(all_categories[main_category]))
        )
        odd_item = random.choice(all_categories[odd_category])

        puzzle_items = main_items + [odd_item]
        random.shuffle(puzzle_items)

        # Build hint based on difficulty
        hint = None
        if hint_available:
            hint = f"Think about what {main_items[0]}, {main_items[1]}, and {main_items[2]} have in common."

        result = {
            "type": "odd_one_out",
            "title": "Which One Doesn't Belong?",
            "instruction": "Circle the word that doesn't fit with the others.",
            "items": puzzle_items,
            "answer": odd_item,
            "difficulty": self.difficulty_level,
        }

        if hint:
            result["hint"] = hint
        if show_explanation:
            result["explanation"] = f"The others are all {main_category}"

        return result
