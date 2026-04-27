"""Cleanup and maintenance tasks."""

import logging
from datetime import datetime, timedelta, timezone

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context

logger = logging.getLogger(__name__)

# Provider run logs older than this are deleted.  Adjust if longer audit trails
# are needed; the table can grow large for high-patient-count deployments.
_LOG_RETENTION_DAYS = 90


@register_task(
    key="scheduler.cleanup_old_run_logs",
    name="Cleanup Old Run Logs",
    default_cron="0 3 * * 0",  # 3:00 AM every Sunday
    description=f"Deletes CareCircleProviderRunLog rows older than {_LOG_RETENTION_DAYS} days.",
    enabled_by_default=True,
    max_instances=1,
    misfire_grace_time=3600,  # 1-hour grace; missing a weekly run is fine
)
async def cleanup_old_run_logs() -> dict:
    """Delete provider run logs older than _LOG_RETENTION_DAYS days."""
    from sqlalchemy import delete
    from app.db.database import async_session_local
    from app.models.care_circle import CareCircleProviderRunLog

    cutoff = datetime.now(timezone.utc) - timedelta(days=_LOG_RETENTION_DAYS)

    async with task_execution_context(
        task_key="scheduler.cleanup_old_run_logs",
        task_name="Cleanup Old Run Logs",
    ) as ctx:
        async with async_session_local() as db:
            stmt = delete(CareCircleProviderRunLog).where(
                CareCircleProviderRunLog.created_at < cutoff
            )
            result = await db.execute(stmt)
            deleted_count = result.rowcount
            await db.commit()

        logger.info("Cleaned up %d provider run log rows (before %s)", deleted_count, cutoff.date())
        ctx["deleted_count"] = deleted_count
        ctx["cutoff_date"] = cutoff.isoformat()

    return {
        "task": "scheduler.cleanup_old_run_logs",
        "status": "success",
        "deleted_count": deleted_count,
        "cutoff_date": cutoff.isoformat(),
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }
