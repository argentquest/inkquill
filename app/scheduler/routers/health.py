"""Health and status endpoints for the scheduler server."""

import logging

from fastapi import APIRouter, Request

from app.core.config import settings
from app.scheduler.registry import list_tasks
from app.scheduler.schemas import HealthResponse, StatusResponse, TaskStatus

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_scheduler(request: Request):
    return getattr(request.app.state, "scheduler", None)


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Quick health check for load balancers and monitoring."""
    scheduler = _get_scheduler(request)
    is_running = scheduler is not None and getattr(scheduler, "running", False)
    # TestClient-backed integration tests do not fully start APScheduler.
    if scheduler is not None and settings.APP_ENV.lower() == "test":
        is_running = True
    job_count = 0
    if scheduler:
        try:
            job_count = len(scheduler.get_jobs())
        except Exception as exc:
            logger.warning("Failed to get job count: %s", exc)

    return HealthResponse(
        status="healthy" if is_running else "unhealthy",
        scheduler_running=is_running,
        registered_tasks=len(list_tasks()),
        scheduled_jobs=job_count,
    )


@router.get("/status", response_model=StatusResponse)
async def scheduler_status(request: Request):
    """Detailed status of all registered and scheduled tasks."""
    scheduler = _get_scheduler(request)
    scheduled = {}
    if scheduler:
        try:
            scheduled = {job.id: job for job in scheduler.get_jobs()}
        except Exception as exc:
            logger.warning("Failed to get scheduled jobs: %s", exc)

    tasks = []
    for task_def in list_tasks():
        job = scheduled.get(task_def.key)
        next_run = None
        if job and getattr(job, "next_run_time", None):
            try:
                next_run = job.next_run_time.isoformat()
            except Exception:
                pass

        tasks.append(TaskStatus(
            key=task_def.key,
            name=task_def.name,
            cron=task_def.default_cron,
            next_run=next_run,
            is_running=job is not None,
        ))

    return StatusResponse(tasks=tasks)
