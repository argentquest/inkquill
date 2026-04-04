import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class WordConnectProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    A word connection puzzle - connect related words.
    Shows pairs of related words, user identifies the connection.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get word connection puzzles.
        
        Returns:
            dict with word connect data
        """
        cfg = self.patient_config
        
        # Word pairs with their connection
        word_pairs = cfg.get("word_pairs", [
            {"word1": "Sun", "word2": "Sky", "connection": "Both are in the sky"},
            {"word1": "Cat", "word2": "Meow", "connection": "Cats say meow"},
            {"word1": "Bread", "word2": "Butter", "connection": "They go together"},
            {"word1": "Day", "word2": "Night", "connection": "Opposites of the day"},
            {"word1": "Dog", "word2": "Bark", "connection": "Dogs bark"},
            {"word1": "Rain", "word2": "Umbrella", "connection": "Keeps you dry"},
            {"word1": "Book", "word2": "Read", "connection": "You read a book"},
            {"word1": "Coffee", "word2": "Morning", "connection": "People drink it in the morning"},
            {"word1": "Snow", "word2": "Winter", "connection": "Happens in winter"},
            {"word1": "Flower", "word2": "Garden", "connection": "Flowers grow in gardens"},
            {"word1": "Phone", "word2": "Call", "connection": "You make a call"},
            {"word1": "Bed", "word2": "Sleep", "connection": "You sleep in a bed"},
            {"word1": "Water", "word2": "Thirst", "connection": "Water quenches thirst"},
            {"word1": "Music", "word2": "Song", "connection": "A song is music"},
            {"word1": "Chair", "word2": "Sit", "connection": "You sit on a chair"},
        ])
        
        # Select 4 random pairs
        selected = random.sample(word_pairs, 4)
        
        return {
            "title": "Word Connect",
            "instruction": "Draw a line to connect the related words!",
            "pairs": selected,
        }