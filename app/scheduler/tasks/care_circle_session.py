"""Daily Care Circle session pre-generation task.

Scheduled at 06:00 daily — before newsletter dispatch (08:00) so that session
content is already assembled when the delivery task runs.

Job tracking
------------
Each patient gets a JobStatus DB row (CRUD in app/crud/job_status.py) so the
frontend can poll for progress.  The job lifecycle is:
  CREATED → RUNNING → COMPLETED | FAILED

Family owner resolution
-----------------------
Sessions must be attributed to a user for permission checks downstream.
_get_family_owner_user_id() uses a three-tier fallback:
  1. family.created_by_user_id  (explicit creator)
  2. FamilyMembership with role='owner', preferring primary=True
  3. patient.created_by_user_id  (last resort)
"""

import logging
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import select

from app.crud import job_status as crud_job_status
from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context
from app.scheduler.tasks._helpers import fetch_active_patients
from app.db.database import async_session_local
from app.models.care_circle import (
    CareCircleFamily,
    CareCircleFamilyMembership,
    CareCirclePatientProfile,
)
from app.models.job_status import JobStateEnum, JobTypeEnum

logger = logging.getLogger(__name__)


async def _get_family_owner_user_id(db, patient: CareCirclePatientProfile) -> int | None:
    """Resolve the user ID to attribute the session job to.

    Returns None only if all three fallback tiers fail, which should be treated
    as a configuration error for the family.
    """
    # Tier 1 — explicit family creator
    family = await db.get(CareCircleFamily, patient.family_id)
    if family and family.created_by_user_id:
        return family.created_by_user_id

    # Tier 2 — membership with role='owner', prefer primary=True
    owner_membership = await db.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.family_id == patient.family_id,
            CareCircleFamilyMembership.role == "owner",
        ).order_by(
            CareCircleFamilyMembership.is_primary.desc(),
            CareCircleFamilyMembership.id.asc(),
        )
    )
    if owner_membership:
        return owner_membership.user_id

    # Tier 3 — whoever created the patient record
    return patient.created_by_user_id


@register_task(
    key="care_circle.daily_session",
    name="Daily Session Pre-generation",
    default_cron="0 6 * * *",  # 06:00 daily
    description="Pre-generates daily Care Circle sessions for all active patients.",
    enabled_by_default=True,
    max_instances=3,
    misfire_grace_time=600,
)
async def pregenerate_daily_sessions(reference_date: date | None = None) -> dict:
    """Pre-generate a daily session for every active patient.

    Args:
        reference_date: Date to generate content for. Defaults to today.
                        Pass a past date to backfill missing sessions.
    """
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    target_date = reference_date or date.today()

    async with task_execution_context(
        task_key="care_circle.daily_session",
        task_name="Daily Session Pre-generation",
    ) as ctx:
        try:
            patients = await fetch_active_patients()
        except Exception as exc:
            logger.error("Failed to fetch active patients: %s", exc, exc_info=True)
            ctx.update({"status": "failed", "error": str(exc), "total_patients": 0, "results": []})
            raise

        logger.info("Pre-generating sessions for %s — %d patients", target_date, len(patients))

        results = []
        success_count = 0
        failure_count = 0

        for patient in patients:
            job_id = str(uuid.uuid4())
            try:
                async with async_session_local() as db:
                    db_patient = await db.get(CareCirclePatientProfile, patient.id)
                    if not db_patient:
                        raise ValueError(f"Patient {patient.id} not found (deleted mid-run?)")

                    owner_user_id = await _get_family_owner_user_id(db, db_patient)
                    if not owner_user_id:
                        raise ValueError(f"No owner user found for patient {patient.id}")

                    await crud_job_status.create_job(
                        db=db,
                        job_id=job_id,
                        user_id=owner_user_id,
                        job_type=JobTypeEnum.CARE_CIRCLE_DAILY_SESSION,
                        status_message=f"Preparing daily session for {db_patient.display_name}.",
                    )
                    await crud_job_status.update_job_status(
                        db, job_id, JobStateEnum.RUNNING,
                        status_message=f"Generating providers for {db_patient.display_name}.",
                    )

                    session_generated = await assemble_daily_patient_session(
                        db, patient.id, job_id=job_id, for_date=target_date,
                    )
                    if not session_generated:
                        raise ValueError(f"Session assembly returned no content for patient {patient.id}")

                    await crud_job_status.update_job_status(
                        db, job_id, JobStateEnum.COMPLETED,
                        status_message=f"Session completed for {db_patient.display_name}.",
                        result_message=f"Generated daily session for patient {db_patient.id}.",
                    )

                results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "status": "generated",
                    "job_id": job_id,
                })
                success_count += 1

            except Exception as exc:
                logger.error("Session generation failed for patient %s: %s", patient.id, exc, exc_info=True)
                # Best-effort status update — don't let a DB failure here mask the original error.
                try:
                    async with async_session_local() as db:
                        await crud_job_status.update_job_status(
                            db, job_id, JobStateEnum.FAILED,
                            status_message=f"Session failed for {patient.display_name}.",
                            result_message=str(exc)[:500],
                        )
                except Exception:
                    logger.warning(
                        "Also failed to update job status to FAILED for patient %s job %s",
                        patient.id, job_id, exc_info=True,
                    )
                results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "status": "failed",
                    "job_id": job_id,
                    "error": str(exc),
                })
                failure_count += 1

        ctx.update({
            "total_patients": len(patients),
            "reference_date": target_date.isoformat(),
            "success_count": success_count,
            "failure_count": failure_count,
        })

    return {
        "task": "care_circle.daily_session",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "reference_date": target_date.isoformat(),
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
