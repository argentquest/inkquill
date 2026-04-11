import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class ColorMatchProvider(BaseCareCircleProvider):
    provider_key = "color_match"
    is_safe_for_patient = True

    """
    A simple color matching game.
    Shows a color and the user guesses which familiar object has that color.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a color matching puzzle.
        
        Returns:
            dict with color puzzle data
        """
        cfg = self.patient_config
        
        # Color-to-object mappings (familiar items for elderly)
        color_pairs = cfg.get("color_pairs", [
            {"color": "Red", "object": "Apple", "options": ["Apple", "Banana", "Grape"]},
            {"color": "Yellow", "object": "Sunflower", "options": ["Sunflower", "Rose", "Tulip"]},
            {"color": "Blue", "object": "Sky", "options": ["Sky", "Grass", "Cloud"]},
            {"color": "Green", "object": "Grass", "options": ["Grass", "Ocean", "Fire"]},
            {"color": "Orange", "object": "Orange", "options": ["Orange", "Apple", "Lemon"]},
            {"color": "Purple", "object": "Grape", "options": ["Grape", "Carrot", "Sky"]},
            {"color": "White", "object": "Snow", "options": ["Snow", "Leaf", "Mud"]},
            {"color": "Brown", "object": "Chocolate", "options": ["Chocolate", "Sky", "Lemon"]},
            {"color": "Pink", "object": "Rose", "options": ["Rose", "Grass", "Ocean"]},
            {"color": "Black", "object": "Night Sky", "options": ["Night Sky", "Snow", "Sun"]},
        ])
        
        # Select a random color puzzle
        puzzle = random.choice(color_pairs)
        
        return {
            "title": "Color Match",
            "instruction": "Which item is " + puzzle["color"].lower() + "?",
            "color": puzzle["color"],
            "answer": puzzle["object"],
            "options": puzzle["options"],
        }
