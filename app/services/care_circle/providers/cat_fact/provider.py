import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict

class CatFactProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Fetches a random cat fact from an external public API.
    
    Also provides a placeholder image URL for rendering in templates.
    """
    
    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Retrieve the cat fact asynchronously.

        Calls the Ninja Cat Fact API. If the network request fails or 
        times out, a static fallback fact is used.

        Returns:
            dict: Containing the text 'fact' and an 'image_url'.
        """
        cfg = self.patient_config
        api_url = cfg.get("api_url", "https://catfact.ninja/fact")
        image_url = cfg.get("image_api", "https://cataas.com/cat")
        fallback = cfg.get("fallback", "Cats sleep for about 70% of their lives. That's about 13-16 hours a day!")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, follow_redirects=True)
                if response.status_code == 200:
                    data = response.json()
                    fact = data.get("fact", fallback)
                    return {"fact": fact, "image_url": image_url}
            return {"fact": fallback, "image_url": image_url}
        except:
            return {"fact": fallback, "image_url": image_url}
