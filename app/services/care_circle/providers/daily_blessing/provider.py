import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class DailyBlessingProvider(BaseCareCircleProvider):
    provider_key = "daily_blessing"
    is_safe_for_patient = True

    """
    Provides a simple, warm blessing or prayer each day.
    Gentle and uplifting content for elderly users.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a daily blessing.
        
        Returns:
            dict with blessing text
        """
        cfg = self.patient_config
        
        blessings = cfg.get("blessings", [
            "May your day be filled with gentle joy and peaceful moments.",
            "You are a blessing to everyone who knows you.",
            "May the warmth of the sun bring a smile to your heart today.",
            "You are loved more than you know.",
            "Today is a gift. Enjoy every moment.",
            "May your heart be light and your spirit be calm.",
            "You bring so much happiness to those around you.",
            "May peace find you wherever you go today.",
            "Your smile makes the world a better place.",
            "You are stronger than you know and loved more than you realize.",
            "May this day bring you moments of quiet happiness.",
            "You are a treasure to your family and friends.",
            "Today, may you feel the warmth of love all around you.",
            "Every day with you is a blessing to us all.",
            "May your heart be filled with gratitude today.",
            "You make the world a kinder place just by being in it.",
            "May the simple pleasures of today bring you great joy.",
            "You are a shining light to everyone who loves you.",
            "Today, know that you are thought of with warmth and care.",
            "May your day be as wonderful as you are.",
        ])
        
        # Day-of-year based selection for consistency
        from datetime import date
        day_of_year = date.today().timetuple().tm_yday
        index = day_of_year % len(blessings)
        
        return {
            "blessing": blessings[index]
        }
