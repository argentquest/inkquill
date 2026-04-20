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

        # Patient profile attributes for the footer summary
        prefs = getattr(patient_profile, "preferences", {}) or {}

        def _list_val(key: str) -> list:
            v = prefs.get(key, [])
            return v if isinstance(v, list) else []

        def _str_val(key: str) -> str:
            return str(prefs.get(key, "") or "").strip()

        delivery_days = getattr(patient_profile, "delivery_days", None) or []
        auth_image_keys = getattr(patient_profile, "auth_image_keys", None) or []

        scalar_fields = []
        for label, value in [
            ("Name", getattr(patient_profile, "display_name", "") or _str_val("recipient_name")),
            ("Stage", getattr(patient_profile, "stage", "") or ""),
            ("Access State", getattr(patient_profile, "access_state", "") or ""),
            ("Timezone", getattr(patient_profile, "timezone", "") or ""),
            ("Preferred Language", getattr(patient_profile, "preferred_language", "") or ""),
            ("Country", getattr(patient_profile, "country", "") or ""),
            ("Postal Code", getattr(patient_profile, "postal_code", "") or ""),
            ("Latitude", getattr(patient_profile, "latitude", "") or ""),
            ("Longitude", getattr(patient_profile, "longitude", "") or ""),
            ("Delivery Time", getattr(patient_profile, "delivery_time", "") or ""),
            ("Email", getattr(patient_profile, "email", "") or ""),
            ("Phone", getattr(patient_profile, "phone_number", "") or ""),
            ("Pronoun", _str_val("preferred_pronoun")),
            ("Era of Youth", _str_val("era_of_youth")),
            ("Hometown", _str_val("hometown")),
            ("Background", _str_val("nationality_or_background")),
            ("Weather City", _str_val("city_for_weather")),
            ("Mobility", _str_val("mobility_level").replace("_", " ").title()),
        ]:
            if value:
                scalar_fields.append({"label": label, "value": value})

        list_fields = []
        for label, key in [
            ("Delivery Days", None),
            ("Auth Images", None),
            ("Family Members", "family_members"),
            ("Life Roles", "life_roles"),
            ("Pets", "pets"),
            ("Hobbies", "hobbies"),
            ("Favourite Activities", "favorite_activities"),
            ("Favourite Foods", "favourite_foods"),
            ("Favourite Singers", "favourite_singers"),
            ("Favourite TV Shows", "favourite_tv_shows"),
        ]:
            if label == "Delivery Days":
                items = delivery_days
            elif label == "Auth Images":
                items = auth_image_keys
            else:
                items = _list_val(key)
            if items:
                list_fields.append({"label": label, "items": items})

        return {
            "disclaimer": disclaimer,
            "total_tokens": total_tokens,
            "total_providers": total_providers,
            "llm_providers": llm_providers,
            "model_used": model_used,
            "elapsed_s": elapsed_s,
            "generation_date": generation_date,
            "scalar_fields": scalar_fields,
            "list_fields": list_fields,
        }
