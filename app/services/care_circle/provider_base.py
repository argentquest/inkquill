"""
Base provider interface for Care Circle.
Migrated from DailyNewsletter but refactored to return strict JSON
rather than HTML, and built to fail safely in a React-driven environment.
"""

from typing import Any, Dict, Optional
import traceback
import logging

logger = logging.getLogger(__name__)

class BaseCareCircleProvider:
    """
    All ported DailyNewsletter providers must inherit from this base class.
    This ensures that execution is uniform, exceptions are trapped safely,
    and output is strictly JSON structured for the React frontend.
    """
    
    # Needs to be overridden by subclasses
    provider_key: str = "base"
    is_safe_for_patient: bool = False

    def __init__(self, patient_config: Optional[Dict[str, Any]] = None):
        """
        :param patient_config: Optional dictionary containing family-managed preferences
        """
        self.patient_config = patient_config or {}

    async def execute(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Public execution wrapper. Wraps the core generation logic
        in a safety net so no LLM failure takes down the patient dashboard.
        """
        try:
            logger.info(f"Executing provider {self.provider_key} for patient {patient_profile.id}")
            result = await self._generate_payload(patient_profile)
            return {
                "success": True,
                "provider_key": self.provider_key,
                "data": result
            }
        except Exception as e:
            logger.error(f"Provider {self.provider_key} failed: {str(e)}")
            logger.error(traceback.format_exc())
            return self._build_fallback_payload(patient_profile, error=str(e))

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        To be implemented by the specific provider.
        Must return a structured dict representing the content map.
        """
        raise NotImplementedError("Subclasses must implement _generate_payload")

    def _build_fallback_payload(self, patient_profile: Any, error: str) -> Dict[str, Any]:
        """
        A safe fallback payload returned when the provider crashes or LLM key expires.
        Ensures the UI can gracefully show an empty state instead of breaking.
        """
        return {
            "success": False,
            "provider_key": self.provider_key,
            "error_detail": error,
            "data": {
                "text": "Content temporarily unavailable.",
                "type": "error_state"
            }
        }
