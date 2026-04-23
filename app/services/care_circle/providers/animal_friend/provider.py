import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.variety_utils import pick_avoiding_recent
from typing import Any, Dict


_DOG_FACTS = [
    "Dogs are loyal friends who love to see their families.",
    "Golden retrievers are known for their friendly and patient nature.",
    "Labrador dogs are wonderful companions who love gentle walks.",
    "Poodles are intelligent dogs who enjoy gentle games and walks.",
    "Beagles are curious hounds who follow interesting scents happily.",
    "Corgis are cheerful little dogs with big personalities.",
    "Dachshunds, also known as sausage dogs, are bold and playful.",
    "Border collies are very intelligent and love learning new things.",
    "Cavalier King Charles spaniels are gentle, affectionate companions.",
    "Shih Tzus were bred to be lap dogs for royalty — and they love cuddles.",
    "Pugs have gentle, loving personalities and enjoy relaxing indoors.",
    "Maltese dogs have silky white coats and are very sweet-natured.",
    "Bichon frises are cheerful little dogs who love to make people laugh.",
    "Whippets are gentle and calm indoors, and they love a cosy spot to nap.",
    "Cocker spaniels have beautiful long ears and a wonderfully kind nature.",
    "Miniature schnauzers are lively, friendly, and love family life.",
    "Basset hounds have long floppy ears and a wonderfully gentle temperament.",
    "Bulldogs are calm, gentle, and very fond of a good rest.",
    "Yorkshire terriers are tiny but full of confidence and affection.",
    "Dalmatians are famous for their spotted coats and playful energy.",
    "Greyhounds are the fastest dogs in the world, but love quiet, lazy naps.",
    "Saint Bernards are famous for their size and their gentle, patient nature.",
    "Jack Russell terriers are small but bursting with enthusiasm and fun.",
    "Shetland sheepdogs, or Shelties, are devoted, gentle, and very loyal.",
    "Chow chows have fluffy lion-like manes and are devoted to their families.",
    "Dobermanns are loyal and protective, and very gentle with loved ones.",
    "Old English sheepdogs are fluffy, lovable, and very good with children.",
    "Springer spaniels love to explore and are full of joy and enthusiasm.",
    "Samoyeds have beautiful white coats and always seem to be smiling.",
    "Every dog, no matter the breed, knows how to show unconditional love.",
    "Dogs have been faithful companions to humans for thousands of years.",
    "A wagging tail is a dog's way of saying 'I am so happy to see you!'",
    "Dogs can recognise their owner's voice among hundreds of others.",
    "The average dog understands around 165 words — some learn even more!",
    "Dogs dream just like humans do — they may even dream about their owners.",
    "A dog's nose is so sensitive it can smell things 100,000 times better than humans.",
    "Puppies are born with their eyes closed and open them after about two weeks.",
    "Dogs have a special muscle in their brow that makes them look adorable when they tilt their heads.",
    "Dogs are known to comfort people who are feeling sad — they really do care.",
    "A dog's heartbeat slows down when they are petted by someone they love.",
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
                            "fact": pick_avoiding_recent(dog_facts, "animal_friend_fact"),
                        }
        except Exception as exc:
            app_logger.warning("animal_friend: dog.ceo fetch failed: %s", exc)

        return {
            "image_url": "",
            "animal": "Dog",
            "fact": pick_avoiding_recent(dog_facts, "animal_friend_fact"),
        }
