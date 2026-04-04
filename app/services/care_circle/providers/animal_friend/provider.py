import random
import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class AnimalFriendProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

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
        
        fallback = cfg.get(
            "fallback",
            "Animals bring so much joy to our lives!"
        )
        
        # Warm animal facts for elderly
        warm_facts = cfg.get("warm_facts", [
            "Dogs are loyal friends who love to see their families.",
            "Cats enjoy warm sunny spots and gentle pets.",
            "Birds sing beautiful songs that brighten our days.",
            "Fish swimming calmly can help us feel peaceful.",
            "Bunnies love gentle strokes and quiet company.",
            "Butterflies remind us that beautiful things come our way.",
            "Horses are gentle giants who sense our feelings.",
            "Dolphins are playful and love to make us smile.",
        ])
        
        try:
            async with httpx.AsyncClient() as client:
                # Get a random dog photo
                response = await client.get(
                    "https://dog.ceo/api/breeds/image/random",
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("message", "")
                    if image_url:
                        return {
                            "image_url": image_url,
                            "animal": "Dog",
                            "fact": random.choice(warm_facts)
                        }
        except Exception:
            pass
        
        # Fallback to static content
        return {
            "image_url": "",
            "animal": "Animal Friend",
            "fact": random.choice(warm_facts)
        }
