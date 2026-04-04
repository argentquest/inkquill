"""
Weather provider adapted for Care Circle patient sessions.
Fetches real weather from wttr.in and generates a warm message.
"""

import httpx
import urllib.parse
import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)

class WeatherProvider(BaseCareCircleProvider):
    provider_key = "weather"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Implementation of the weather fetch logic.
        """
        # In a real environment, preferences are a parsed JSON dict off the patient_profile
        prefs = getattr(patient_profile, "preferences", {}) or {}
        city = prefs.get("city_for_weather", self.patient_config.get("default_city", "Unknown"))
        recipient_name = getattr(patient_profile, "display_name", "Friend")
        fallback_msg = self.patient_config.get("fallback", "Weather currently unavailable.")
        
        if not city or city == "Unknown":
            return {
                "text": "Weather unavailable. Please set a city in the Family portal.",
                "subheading": "Update Profile",
                "type": "weather",
                "city": "Unknown"
            }

        try:
            city_encoded = urllib.parse.quote(city)
            url = f"https://wttr.in/{city_encoded}?format=j1"

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, headers={"Accept": "application/json"})
                resp.raise_for_status()
                data = resp.json()
                
                current = data.get("current_condition", [{}])[0]
                temp_f = current.get("temp_F", "--")
                desc = current.get("weatherDesc", [{}])[0].get("value", "Clear")
                
                raw_weather = f"{temp_f}°F and {desc}"
                
                # NOTE: For Sprint 02, we bypass LLM direct invocation here until
                # the OpenRouter client logic is refactored for Care Circle async jobs.
                # Returning the formatted string matching what the LLM *would* construct.
                generated_msg = f"Good morning, {recipient_name}! It is {raw_weather} in {city} today."
                
                return {
                    "text": generated_msg,
                    "subheading": f"{city} Weather",
                    "type": "weather",
                    "temperature": temp_f,
                    "condition": desc
                }

        except Exception as e:
            logger.warning(f"Weather fetch failed for city {city}: {e}")
            return {
                "text": fallback_msg,
                "subheading": "Weather",
                "type": "weather",
                "city": city
            }
