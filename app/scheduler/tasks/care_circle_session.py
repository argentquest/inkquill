"""Daily Care Circle session pre-generation task."""

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


@register_task(
    key="care_circle.daily_session",
    name="Daily Session Pre-generation",
    default_cron="0 6 * * *",  # 6:00 AM daily (before newsletter)
    description="Pre-generates daily sessions for all active patients.",
    enabled_by_default=True,
    max_instances=3,
    misfire_grace_time=600,
)
async def pregenerate_daily_sessions() -> dict:
    """Pre-generate daily sessions for all active patients."""
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    async with task_execution_context(
        task_key="care_circle.daily_session",
        task_name="Daily Session Pre-generation",
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

        logger.info("Pre-generating daily sessions for %d patients", len(patients))

        results = []
        success_count = 0
        failure_count = 0

        for patient in patients:
            try:
                session_data = await assemble_daily_patient_session(patient.id)
                results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "status": "generated",
                    "highlights_count": len(session_data.get("highlights", [])),
                })
                success_count += 1
            except Exception as exc:
                logger.error(
                    "Failed to generate session for patient %s: %s",
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
        "task": "care_circle.daily_session",
        "executed_at": datetime.utcnow().isoformat(),
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
