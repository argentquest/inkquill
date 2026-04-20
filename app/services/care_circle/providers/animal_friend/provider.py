import random
import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


_DOG_FACTS = [
    "Dogs are loyal friends who love to see their families.",
    "Golden retrievers are known for their friendly and patient nature.",
    "Labrador dogs are wonderful companions who love gentle walks.",
    "Poodles are intelligent dogs who enjoy gentle games and walks.",
    "Beagles are curious hounds who follow interesting scents happily.",
    "Corgis are cheerful little dogs with big personalities.",
]


class AnimalFriendProvider(BaseCareCircleProvider):
    provider_key = "animal_friend"
    is_safe_for_patient = True

    """
    Shows a friendly animal photo with a warm fact.
    Uses dog CEO API and provides warm, friendly content.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a friendly animal photo and fact.
        
        Returns:
            dict with animal data
        """
        cfg = self.patient_config
        
        dog_facts = cfg.get("dog_facts", _DOG_FACTS)
        
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get("https://dog.ceo/api/breeds/image/random")
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("message", "")
                    if image_url:
                        return {
                            "image_url": image_url,
                            "animal": "Dog",
                            "fact": random.choice(dog_facts),
                        }
        except Exception as exc:
            app_logger.warning("animal_friend: dog.ceo fetch failed: %s", exc)

        return {
            "image_url": "",
            "animal": "Dog",
            "fact": random.choice(dog_facts),
        }
