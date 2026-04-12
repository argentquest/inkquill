import random
import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


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
            "Golden retrievers are known for their friendly and patient nature.",
            "Tabby cats often purr loudly when they feel safe and content.",
            "Parrots can learn to mimic sounds and bring joy with their chatter.",
            "Tropical fish come in brilliant colors that delight the eyes.",
            "Guinea pigs enjoy gentle company and soft hay to nibble.",
            "Hummingbirds hover gracefully and visit flowers for sweet nectar.",
            "Elephants have remarkable memories and never forget their friends.",
            "Sea turtles glide through water with peaceful elegance.",
            "Labrador dogs are wonderful companions who love gentle walks.",
            "Persian cats have soft fluffy coats that are lovely to stroke.",
            "Canaries fill the room with cheerful morning melodies.",
            "Goldfish enjoy calm waters and peaceful surroundings.",
            "Hamsters store food in their cheeks and look quite adorable.",
            "Dragonflies dance above ponds on warm summer afternoons.",
            "Sheep are gentle flock animals who enjoy grazing together.",
            "Penguins waddle charmingly and care for their families devotedly.",
            "Poodles are intelligent dogs who love gentle games and walks.",
            "Siamese cats are vocal and enjoy chatting with their owners.",
            "Finches hop cheerfully and sing sweet little tunes.",
            "Koi fish grow quite large and recognize their keepers.",
            "Tortoises live long peaceful lives and enjoy leafy greens.",
            "Beagles are curious hounds who follow interesting scents happily.",
            "Ragdoll cats go limp when held and are wonderfully relaxed.",
            "Budgies are small parrots that love to chirp and play.",
            "Betta fish display beautiful flowing fins and calm swimming.",
            "Ferrets are playful creatures who love to explore and tumble.",
            "Swans glide gracefully across lakes in elegant pairs.",
            "Corgis are cheerful little dogs with big personalities.",
            "Maine Coon cats are gentle giants who enjoy family time.",
            "Robins visit gardens and sing cheerful spring songs.",
            "Angelfish swim serenely and add beauty to any tank.",
            "Rabbits thump their feet when excited and hop with joy.",
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
