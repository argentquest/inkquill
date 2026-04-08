import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class BingoProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    A 5x5 bingo card with familiar words.
    Designed for elderly users with familiar, easy-to-recognize items.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a bingo card with familiar words.
        
        Returns:
            dict with bingo card data
        """
        cfg = self.patient_config
        
        # Familiar words for elderly (25 words for 5x5 card)
        # Center is FREE space
        word_bank = cfg.get("word_bank", [
            "Sun", "Moon", "Star", "Cloud", "Rain",
            "Dog", "Cat", "Bird", "Fish", "Tree",
            "Apple", "Bread", "Milk", "Tea", "Cake",
            "Book", "Chair", "Clock", "Phone", "Light",
            "Home", "Love", "Joy", "Peace", "Friend",
            "Song", "Dance", "Flower", "Garden", "Morning"
        ])
        
        # Shuffle and take 24 words (center is free)
        words = random.sample(word_bank, 24)
        
        # Insert FREE in the middle (position 12)
        words.insert(12, "FREE")
        
        # Split into 5 rows
        card = []
        for i in range(5):
            row = words[i*5:(i+1)*5]
            card.append(row)
        
        return {
            "title": "Bingo Time!",
            "instruction": "Mark the words as you find them in today's newsletter!",
            "card": card,
        }
