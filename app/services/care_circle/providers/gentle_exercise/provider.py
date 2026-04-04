import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict

class GentleExerciseProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    Provides a simple, low-impact exercise recommendation via static configuration.
    """
    
    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Select a gentle exercise from the predefined list.

        Returns:
            dict: Containing exercise 'name', 'steps', and its 'benefit'.
        """
        cfg = self.patient_config
        exercises = cfg.get("exercises", [
            {"name": "Seated Arm Raise", "steps": "Sit comfortably. Slowly raise both arms above your head. Hold for 5 seconds. Lower slowly. Repeat 3 times.", "benefit": "Improves shoulder mobility and circulation."}
        ])
        selected = random.choice(exercises)
        return selected
