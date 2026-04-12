"""
Newsletter Footer provider for Care Circle patient sessions.

Renders a footer with a configurable disclaimer and generation statistics
(total tokens, model, provider count, elapsed time). Stats are passed in
via patient_config after all other providers have run.
"""

import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)


class NewsletterFooterProvider(BaseCareCircleProvider):
    provider_key = "newsletter_footer"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config

        disclaimer = cfg.get("disclaimer", (
            "This newsletter is generated for personal care and wellbeing purposes only "
            "and does not constitute medical advice. Content is AI-assisted and reviewed "
            "with care. Please consult a qualified healthcare professional for any medical guidance."
        ))

        # Generation statistics — provided by the test runner after all providers complete
        total_tokens = cfg.get("total_tokens", 0)
        total_providers = cfg.get("total_providers", 0)
        llm_providers = cfg.get("llm_providers", 0)
        model_used = cfg.get("model_used", "")
        elapsed_s = cfg.get("elapsed_s", 0.0)
        generation_date = cfg.get("generation_date", "")

        return {
            "disclaimer": disclaimer,
            "total_tokens": total_tokens,
            "total_providers": total_providers,
            "llm_providers": llm_providers,
            "model_used": model_used,
            "elapsed_s": elapsed_s,
            "generation_date": generation_date,
        }
