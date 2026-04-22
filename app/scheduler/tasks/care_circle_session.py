"""Daily Care Circle session pre-generation task."""

import logging
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import select

from app.crud import job_status as crud_job_status
from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context
from app.db.database import async_session_local
from app.models.care_circle import (
    CareCircleFamily,
    CareCircleFamilyMembership,
    CareCirclePatientProfile,
)
from app.models.job_status import JobStateEnum, JobTypeEnum

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


async def _get_family_owner_user_id(db, patient: CareCirclePatientProfile) -> int | None:
    family = await db.get(CareCircleFamily, patient.family_id)
    if family and family.created_by_user_id:
        return family.created_by_user_id

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

    return patient.created_by_user_id


@register_task(
    key="care_circle.daily_session",
    name="Daily Session Pre-generation",
    default_cron="0 6 * * *",  # 6:00 AM daily (before newsletter)
    description="Pre-generates daily sessions for all active patients.",
    enabled_by_default=True,
    max_instances=3,
    misfire_grace_time=600,
)
async def pregenerate_daily_sessions(reference_date: date | None = None) -> dict:
    """Pre-generate daily sessions for all active patients."""
    from app.services.care_circle.session_assembler import assemble_daily_patient_session
    target_date = reference_date or date.today()

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
            job_id = str(uuid.uuid4())
            try:
                async with async_session_local() as db:
                    db_patient = await db.get(CareCirclePatientProfile, patient.id)
                    if not db_patient:
                        raise ValueError(f"Patient {patient.id} no longer exists")

                    owner_user_id = await _get_family_owner_user_id(db, db_patient)
                    if not owner_user_id:
                        raise ValueError(
                            f"No family owner user found for patient {patient.id}"
                        )

                    await crud_job_status.create_job(
                        db=db,
                        job_id=job_id,
                        user_id=owner_user_id,
                        job_type=JobTypeEnum.CARE_CIRCLE_DAILY_SESSION,
                        status_message=(
                            f"Preparing daily Care Circle session for patient "
                            f"{db_patient.display_name}."
                        ),
                    )
                    await crud_job_status.update_job_status(
                        db,
                        job_id,
                        JobStateEnum.RUNNING,
                        status_message=(
                            f"Generating Care Circle providers for patient "
                            f"{db_patient.display_name}."
                        ),
                    )

                    session_generated = await assemble_daily_patient_session(
                        db,
                        patient.id,
                        job_id=job_id,
                        for_date=target_date,
                    )
                    if not session_generated:
                        raise ValueError(
                            f"Session assembly returned no content for patient {patient.id}"
                        )

                    await crud_job_status.update_job_status(
                        db,
                        job_id,
                        JobStateEnum.COMPLETED,
                        status_message=(
                            f"Daily Care Circle session completed for patient "
                            f"{db_patient.display_name}."
                        ),
                        result_message=(
                            f"Generated daily session content for patient "
                            f"{db_patient.id}."
                        ),
                    )

                results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "status": "generated",
                    "job_id": job_id,
                })
                success_count += 1
            except Exception as exc:
                logger.error(
                    "Failed to generate session for patient %s: %s",
                    patient.id, exc, exc_info=True,
                )
                try:
                    async with async_session_local() as db:
                        await crud_job_status.update_job_status(
                            db,
                            job_id,
                            JobStateEnum.FAILED,
                            status_message=(
                                f"Daily Care Circle session failed for patient "
                                f"{patient.display_name}."
                            ),
                            result_message=str(exc)[:500],
                        )
                except Exception:
                    logger.warning(
                        "Failed to update job status to FAILED for patient %s job %s",
                        patient.id,
                        job_id,
                        exc_info=True,
                    )
                results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "status": "failed",
                    "job_id": job_id,
                    "error": str(exc),
                })
                failure_count += 1

        ctx["total_patients"] = len(patients)
        ctx["reference_date"] = target_date.isoformat()
        ctx["success_count"] = success_count
        ctx["failure_count"] = failure_count
        ctx["results"] = results

    return {
        "task": "care_circle.daily_session",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "reference_date": target_date.isoformat(),
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
