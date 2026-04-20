"""Shared service to generate and deliver Care Circle newsletters.

Single entry point used by both the scheduler and on-demand frontend triggers.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.care_circle.session_assembler import assemble_daily_patient_session
from app.services.care_circle.newsletter_email_service import send_newsletter_email

logger = logging.getLogger(__name__)


async def deliver_newsletter_to_patient(
    db: AsyncSession,
    patient: Any,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """
    Assemble and send the daily newsletter to a single patient.

    Args:
        db: Active async DB session.
        patient: CareCirclePatientProfile ORM object (already loaded by caller).
        force_regenerate: If True, bypasses the provider cache.

    Returns:
        dict with keys: success, patient_id, email_sent, sms_sent, message
    """
    patient_id: int = patient.id
    patient_name: str = getattr(patient, "display_name", "Unknown")

    try:
        session_data = await assemble_daily_patient_session(db, patient_id)

        if not session_data or not isinstance(session_data, dict) or not session_data.get("success"):
            logger.warning("Newsletter assembly failed for patient %s", patient_id)
            return {
                "success": False,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "reason": "assembly_failed",
                "message": "Failed to assemble newsletter content",
                "email_sent": False,
                "sms_sent": False,
            }

        html_content = session_data.get("html", "")
        if not html_content:
            logger.warning("No HTML content generated for patient %s", patient_id)
            return {
                "success": False,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "reason": "no_html",
                "message": "Newsletter assembled but produced no HTML",
                "email_sent": False,
                "sms_sent": False,
            }

        email_sent = False
        if getattr(patient, "email", None):
            email_result = await send_newsletter_email(patient, html_content)
            email_sent = bool(email_result.get("success"))
            logger.info("Email to %s (%s): sent=%s", patient_name, patient.email, email_sent)

        sms_sent = False
        if getattr(patient, "phone_number", None):
            try:
                from app.services.care_circle.newsletter_sms_service import send_sms_newsletter
                sms_result = await send_sms_newsletter(patient, session_data.get("provider_results", []))
                sms_sent = bool(sms_result.get("success"))
                logger.info("SMS to %s (%s): sent=%s", patient_name, patient.phone_number, sms_sent)
            except Exception as exc:
                logger.error("SMS delivery failed for patient %s: %s", patient_id, exc)

        return {
            "success": email_sent or sms_sent,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "status": "sent",
            "email_sent": email_sent,
            "sms_sent": sms_sent,
            "message": "Newsletter dispatched",
        }

    except Exception as exc:
        logger.error("Failed to deliver newsletter to patient %s: %s", patient_id, exc, exc_info=True)
        return {
            "success": False,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "reason": "exception",
            "message": str(exc),
            "email_sent": False,
            "sms_sent": False,
        }
