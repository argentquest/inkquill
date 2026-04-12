"""Cleanup and maintenance tasks."""

import logging
from datetime import datetime, timedelta

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context

logger = logging.getLogger(__name__)


@register_task(
    key="scheduler.cleanup_old_run_logs",
    name="Cleanup Old Run Logs",
    default_cron="0 3 * * 0",  # 3:00 AM every Sunday
    description="Cleans up old provider run logs older than 90 days.",
    enabled_by_default=True,
    max_instances=1,
    misfire_grace_time=3600,
)
async def cleanup_old_run_logs() -> dict:
    """Clean up provider run logs older than 90 days."""
    from sqlalchemy import delete
    from app.db.database import async_session_local
    from app.models.care_circle import CareCircleProviderRunLog

    cutoff_date = datetime.utcnow() - timedelta(days=90)

    async with task_execution_context(
        task_key="scheduler.cleanup_old_run_logs",
        task_name="Cleanup Old Run Logs",
    ) as ctx:
        try:
            async with async_session_local() as db:
                stmt = delete(CareCircleProviderRunLog).where(
                    CareCircleProviderRunLog.created_at < cutoff_date
                )
                result = await db.execute(stmt)
                deleted_count = result.rowcount
                await db.commit()

            logger.info("Cleaned up %d old run logs (before %s)", deleted_count, cutoff_date)
            ctx["deleted_count"] = deleted_count
            ctx["cutoff_date"] = cutoff_date.isoformat()

        except Exception as exc:
            logger.error("Failed to cleanup old run logs: %s", exc, exc_info=True)
            ctx["deleted_count"] = 0
            ctx["cutoff_date"] = cutoff_date.isoformat()
            raise

    return {
        "task": "scheduler.cleanup_old_run_logs",
        "status": "success",
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date.isoformat(),
        "executed_at": datetime.utcnow().isoformat(),
    }
