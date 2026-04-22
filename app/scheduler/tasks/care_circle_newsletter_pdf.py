"""Daily Care Circle newsletter PDF generation task."""

import logging
from datetime import date, datetime, timezone

from sqlalchemy import select

from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile
from app.scheduler.logging import task_execution_context
from app.scheduler.registry import register_task

logger = logging.getLogger(__name__)


async def _fetch_active_patients():
    """Fetch all active patient profiles."""
    async with async_session_local() as db:
        patient_rows = (
            await db.execute(
                select(CareCirclePatientProfile).where(
                    CareCirclePatientProfile.access_state == "active"
                )
            )
        ).scalars().all()
        return list(patient_rows)


@register_task(
    key="care_circle.daily_newsletter_pdf",
    name="Daily Care Circle Newsletter PDF",
    default_cron="0 7 * * *",
    description="Builds a newsletter.pdf file for every active patient from the daily Care Circle content cache.",
    enabled_by_default=True,
    max_instances=2,
    misfire_grace_time=600,
)
async def generate_daily_newsletter_pdfs(reference_date: date | None = None) -> dict:
    """Generate newsletter PDFs for all active patients."""
    from app.services.care_circle.newsletter_pdf_service import newsletter_pdf_service
    from app.services.care_circle.session_assembler import (
        assemble_daily_patient_session,
        get_newsletter_html_for_date,
    )

    for_date = reference_date or date.today()

    async with task_execution_context(
        task_key="care_circle.daily_newsletter_pdf",
        task_name="Daily Care Circle Newsletter PDF",
    ) as ctx:
        patients = await _fetch_active_patients()
        logger.info("Generating Care Circle newsletter PDFs for %d patients", len(patients))

        results = []
        success_count = 0
        failure_count = 0

        for patient in patients:
            try:
                async with async_session_local() as db:
                    html = await get_newsletter_html_for_date(db, patient.id, for_date)
                    if not html:
                        await assemble_daily_patient_session(
                            db,
                            patient.id,
                            for_date=for_date,
                        )

                    artifact_paths = await newsletter_pdf_service.generate_artifacts_for_patient_date(
                        db,
                        patient.id,
                        for_date,
                    )

                results.append(
                    {
                        "patient_id": patient.id,
                        "patient_name": patient.display_name,
                        "status": "generated",
                        "pdf_path": str(artifact_paths["pdf_path"]),
                        "html_path": str(artifact_paths["html_path"]),
                    }
                )
                success_count += 1
            except Exception as exc:
                logger.error(
                    "Failed to generate newsletter PDF for patient %s: %s",
                    patient.id,
                    exc,
                    exc_info=True,
                )
                results.append(
                    {
                        "patient_id": patient.id,
                        "patient_name": patient.display_name,
                        "status": "failed",
                        "error": str(exc),
                    }
                )
                failure_count += 1

        ctx["for_date"] = for_date.isoformat()
        ctx["total_patients"] = len(patients)
        ctx["success_count"] = success_count
        ctx["failure_count"] = failure_count
        ctx["results"] = results

    return {
        "task": "care_circle.daily_newsletter_pdf",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "for_date": for_date.isoformat(),
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
