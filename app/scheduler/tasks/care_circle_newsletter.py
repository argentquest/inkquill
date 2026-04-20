"""Daily Care Circle newsletter dispatch task."""

import logging
from datetime import datetime
from sqlalchemy import select

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context
from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile

logger = logging.getLogger(__name__)


async def _fetch_active_patients():
    """Fetch all active patient profiles."""
    async with async_session_local() as db:
        patient_rows = (await db.execute(
            select(CareCirclePatientProfile).where(
                CareCirclePatientProfile.access_state == "active"
            )
        )).scalars().all()
        return list(patient_rows)


async def _send_to_patient(patient) -> dict:
    """Send newsletter to a single patient."""
    from app.services.care_circle.newsletter_delivery_service import deliver_newsletter_to_patient
    from app.db.database import async_session_local

    async with async_session_local() as db:
        return await deliver_newsletter_to_patient(db, patient)


@register_task(
    key="care_circle.daily_newsletter",
    name="Daily Care Circle Newsletter",
    default_cron="0 8 * * *",  # 8:00 AM daily
    description="Assembles and sends daily newsletter to all active patients via email and SMS.",
    enabled_by_default=True,
    max_instances=3,
    misfire_grace_time=600,
)
async def dispatch_daily_newsletter() -> dict:
    """Send daily newsletter to all active patients."""
    async with task_execution_context(
        task_key="care_circle.daily_newsletter",
        task_name="Daily Care Circle Newsletter",
    ) as ctx:
        try:
            patients = await _fetch_active_patients()
        except Exception as exc:
            logger.error("Failed to fetch active patients: %s", exc, exc_info=True)
            ctx["status"] = "failed"
            ctx["error"] = f"Database error: {exc}"
            ctx["total_patients"] = 0
            ctx["results"] = []
            raise

        logger.info("Dispatching daily newsletter to %d patients", len(patients))

        results = []
        success_count = 0
        failure_count = 0

        for patient in patients:
            try:
                result = await _send_to_patient(patient)
                results.append(result)
                success_count += 1
            except Exception as exc:
                logger.error(
                    "Failed to send newsletter to patient %s: %s",
                    patient.id, exc, exc_info=True,
                )
                results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "status": "failed",
                    "error": str(exc),
                })
                failure_count += 1

        ctx["total_patients"] = len(patients)
        ctx["success_count"] = success_count
        ctx["failure_count"] = failure_count
        ctx["results"] = results

    return {
        "task": "care_circle.daily_newsletter",
        "executed_at": datetime.utcnow().isoformat(),
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
