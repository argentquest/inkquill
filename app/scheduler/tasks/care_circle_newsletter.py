"""Daily Care Circle newsletter dispatch task.

Scheduled at 08:00 daily — after the session pre-generation (06:00) and PDF
rendering (07:00) have already run, so the newsletter delivery can reference
completed session artifacts.

Fan-out model
-------------
1. Fetch all active patients in a single query.
2. For each patient, call deliver_newsletter_to_patient() in sequence.
   Individual failures are caught and recorded so one bad patient doesn't
   abort the entire batch.
3. Return a summary dict with per-patient results for the admin UI.

max_instances=3 allows up to three concurrent scheduled executions (e.g. if a
manual trigger overlaps with the scheduled run).  Delivery itself is sequential
within each execution.
"""

import logging
from datetime import date, datetime, timezone
from sqlalchemy import select

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context
from app.scheduler.tasks._helpers import fetch_active_patients

logger = logging.getLogger(__name__)


async def _send_to_patient(patient, reference_date: date) -> dict:
    """Deliver the newsletter for *patient* on *reference_date*.

    Opens its own DB session so the delivery service has a clean transaction
    scope independent of the outer patient-loop session.
    """
    from app.services.care_circle.newsletter_delivery_service import deliver_newsletter_to_patient
    from app.db.database import async_session_local

    async with async_session_local() as db:
        return await deliver_newsletter_to_patient(db, patient, reference_date)


@register_task(
    key="care_circle.daily_newsletter",
    name="Daily Care Circle Newsletter",
    default_cron="0 8 * * *",  # 08:00 daily
    description="Assembles and sends the daily newsletter to all active patients via email and SMS.",
    enabled_by_default=True,
    max_instances=3,
    misfire_grace_time=600,  # 10-minute grace — missing the exact 8 AM slot is acceptable
)
async def dispatch_daily_newsletter(reference_date: date | None = None) -> dict:
    """Send the daily newsletter to every active patient.

    Args:
        reference_date: Override the date used for content selection.
                        Defaults to today.  Pass a past date to backfill.
    """
    target_date = reference_date or date.today()

    async with task_execution_context(
        task_key="care_circle.daily_newsletter",
        task_name="Daily Care Circle Newsletter",
    ) as ctx:
        try:
            patients = await fetch_active_patients()
        except Exception as exc:
            logger.error("Failed to fetch active patients: %s", exc, exc_info=True)
            ctx.update({"status": "failed", "error": str(exc), "total_patients": 0, "results": []})
            raise

        logger.info("Dispatching newsletter for %s to %d patients", target_date, len(patients))

        results = []
        success_count = 0
        failure_count = 0

        for patient in patients:
            try:
                result = await _send_to_patient(patient, target_date)
                results.append(result)
                success_count += 1
            except Exception as exc:
                logger.error("Newsletter failed for patient %s: %s", patient.id, exc, exc_info=True)
                results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "status": "failed",
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
        "task": "care_circle.daily_newsletter",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "reference_date": target_date.isoformat(),
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
