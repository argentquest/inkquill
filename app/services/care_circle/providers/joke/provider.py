import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict

class JokeProvider(BaseCareCircleProvider):
    provider_key = "joke"
    is_safe_for_patient = True

    """
    Fetches a safe, single-line joke from an external public API.
    """
    
    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Retrieve a joke asynchronously.

        Calls the JokeAPI in 'safe-mode'. If the network request fails, 
        a static fallback joke is utilized.

        Returns:
            dict: Containing the 'joke' string.
        """
        cfg = self.patient_config
        api_url = cfg.get("api_url", "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single")
        fallback = cfg.get("fallback", "Why did the scarecrow win an award? Because he was outstanding in his field!")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("joke"):
                        return {"joke": data["joke"]}
                return {"joke": fallback}
        except:
            return {"joke": fallback}
