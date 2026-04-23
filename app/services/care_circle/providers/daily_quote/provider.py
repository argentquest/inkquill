"""
Daily quote provider adapted for Care Circle patient sessions.
Fetches from an external API, falling back safely.
"""

import httpx
import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)

class DailyQuoteProvider(BaseCareCircleProvider):
    provider_key = "daily_quote"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Implementation of the quote fetch logic.
        """
        # Pull family configs or use defaults
        api_url = self.patient_config.get("api_url", "https://zenquotes.io/api/random")
        fallback_quote = self.patient_config.get("fallback_quote", "Every day is a new beginning.")
        fallback_author = self.patient_config.get("fallback_author", "Unknown")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(api_url, follow_redirects=True)
                response.raise_for_status()
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    quote = data[0].get("q", fallback_quote)
                    author = data[0].get("a", fallback_author)
                    return {
                        "text": f'"{quote}"',
                        "subheading": f"- {author}",
                        "type": "daily_quote"
                    }
        except Exception as e:
            logger.warning(f"DailyQuoteProvider API failed, using fallback. Error: {e}")
        
        # Fallback payload natively returned if try/except caught or network dropped
        return {
            "text": f'"{fallback_quote}"',
            "subheading": f"- {fallback_author}",
            "type": "daily_quote"
        }
