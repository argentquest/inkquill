import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict

class DailyAffirmationProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    Fetches a daily POSITIVE affirmation from an external public API.
    """
    
    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Retrieve the daily affirmation asynchronously.

        Calls the affirmations.dev API. If the network request fails, 
        a static fallback affirmation is utilized.

        Returns:
            dict: Containing the 'affirmation' string.
        """
        cfg = self.patient_config
        api_url = cfg.get("api_url", "https://www.affirmations.dev/")
        fallback = cfg.get("fallback", "You are loved. You are enough. You matter.")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, follow_redirects=True)
                if response.status_code == 200:
                    data = response.json()
                    return {"affirmation": data.get("affirmation", fallback)}
            return {"affirmation": fallback}
        except:
            return {"affirmation": fallback}
