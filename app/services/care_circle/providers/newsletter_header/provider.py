"""
Newsletter Header provider for Care Circle patient sessions.

Renders a visually styled header banner showing the patient's name, family name,
and the date/time the newsletter was generated. Static provider — no LLM required.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)


class NewsletterHeaderProvider(BaseCareCircleProvider):
    provider_key = "newsletter_header"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = self.get_patient_preferences(patient_profile)

        patient_name = getattr(patient_profile, "display_name", "Friend")

        # Family name: DB column first, then config override, then preferences fallback
        family_name = (
            getattr(patient_profile, "family_name", None)
            or cfg.get("family_name")
            or prefs.get("family_name")
            or ""
        )

        generated_at = datetime.now().strftime("%B %d, %Y  \u2022  %I:%M %p")

        return {
            "patient_name": patient_name,
            "family_name": family_name,
            "generated_at": generated_at,
        }
