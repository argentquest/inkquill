import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict

class DogPhotoProvider(BaseCareCircleProvider):
    provider_key = "dog_photo"
    is_safe_for_patient = True

    """
    Fetches a random picture of a dog from the public Dog API.
    
    Attempts to parse the specific dog breed from the URL structure
    to provide context alongside the image.
    """
    
    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Retrieve the dog photo asynchronously.

        Calls the dog.ceo API. If the network request fails, static 
        fallback content (an empty URL with a default caption) is used.

        Returns:
            dict: Containing 'image_url', 'breed', and 'caption'.
        """
        cfg = self.patient_config
        api_url = cfg.get("api_url", "https://dog.ceo/api/breeds/image/random")
        caption = cfg.get("default_caption", "Here's a friendly pup to brighten your day!")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, follow_redirects=True)
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("message", "")
                    if image_url:
                        # Extract breed from URL path: .../breeds/hound-basset/image.jpg
                        parts = image_url.split("/")
                        breed_idx = parts.index("breeds") + 1 if "breeds" in parts else -1
                        breed = parts[breed_idx].replace("-", " ").title() if breed_idx > 0 else "Dog"
                        return {"image_url": image_url, "breed": breed, "caption": caption}
            return {"image_url": "", "breed": "", "caption": caption}
        except:
            return {"image_url": "", "breed": "", "caption": caption}
