"""Shared service to generate and deliver Care Circle newsletters.

Single entry point used by both the scheduler and on-demand frontend triggers.
"""

import logging
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.care_circle.session_assembler import assemble_daily_patient_session
from app.services.care_circle.newsletter_email_service import send_newsletter_email

logger = logging.getLogger(__name__)


async def deliver_newsletter_to_patient(
    db: AsyncSession,
    patient: Any,
    reference_date: date,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """
    Assemble and send the daily newsletter to a single patient.

    Args:
        db: Active async DB session.
        patient: CareCirclePatientProfile ORM object (already loaded by caller).
        force_regenerate: If True, bypasses the provider cache.

    Returns:
        dict with keys: success, patient_id, email_sent, message
    """
    patient_id: int = patient.id
    patient_name: str = getattr(patient, "display_name", "Unknown")
    patient_email: str | None = getattr(patient, "email", None)

    logger.info(
        "[deliver] START patient_id=%s name=%r email=%s date=%s force=%s",
        patient_id, patient_name, patient_email or "(none)", reference_date, force_regenerate,
    )

    try:
        logger.info("[deliver] calling assemble_daily_patient_session ...")
        session_data = await assemble_daily_patient_session(
            db,
            patient_id,
            force_regenerate=force_regenerate,
            for_date=reference_date,
        )
        logger.info(
            "[deliver] assemble returned type=%s value=%s",
            type(session_data).__name__,
            session_data if not isinstance(session_data, dict) else {k: v for k, v in session_data.items() if k != "html"},
        )

        if not session_data or not isinstance(session_data, dict) or not session_data.get("success"):
            logger.warning(
                "[deliver] assembly failed or returned no dict — patient=%s session_data=%r",
                patient_id, session_data,
            )
            return {
                "success": False,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "reason": "assembly_failed",
                "message": "Failed to assemble newsletter content",
                "email_sent": False,
            }

        html_content = session_data.get("html", "")
        logger.info(
            "[deliver] html_content length=%d card_count=%s",
            len(html_content), session_data.get("card_count"),
        )
        if not html_content:
            logger.warning("[deliver] no HTML produced for patient=%s", patient_id)
            return {
                "success": False,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "reason": "no_html",
                "message": "Newsletter assembled but produced no HTML",
                "email_sent": False,
            }

        email_sent = False
        if patient_email:
            logger.info("[deliver] sending email to %s (%s) ...", patient_name, patient_email)
            try:
                email_result = await send_newsletter_email(
                    patient,
                    html_content,
                    reference_date,
                )
                email_sent = bool(email_result.get("success"))
                logger.info(
                    "[deliver] send_newsletter_email result: sent=%s result=%s",
                    email_sent, email_result,
                )
            except Exception as email_exc:
                logger.error(
                    "[deliver] send_newsletter_email raised an exception for patient=%s: %s",
                    patient_id, email_exc, exc_info=True,
                )
        else:
            logger.info("[deliver] no email address on patient=%s — skipping send", patient_id)

        logger.info("[deliver] DONE patient=%s email_sent=%s", patient_id, email_sent)
        return {
            "success": email_sent,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "status": "sent",
            "email_sent": email_sent,
            "message": "Newsletter dispatched" if email_sent else "Newsletter assembled but no email sent (no address configured)",
        }

    except Exception as exc:
        logger.error(
            "[deliver] UNHANDLED exception for patient=%s: %s",
            patient_id, exc, exc_info=True,
        )
        return {
            "success": False,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "reason": "exception",
            "message": str(exc),
            "email_sent": False,
        }
