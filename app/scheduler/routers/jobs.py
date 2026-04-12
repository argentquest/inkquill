"""Job management API — trigger, pause, resume, reschedule."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.scheduler.main import scheduler
from app.scheduler.registry import get_task, list_tasks
from app.scheduler.schemas import JobListResponse, JobInfo, JobResult, RescheduleRequest
from app.scheduler.logging import log_job_operation

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_scheduler_available():
    """Raise 503 if the scheduler is not initialized."""
    if scheduler is None:
        raise HTTPException(
            status_code=503,
            detail="Scheduler service is not initialized",
        )


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs():
    """List all currently scheduled jobs."""
    _validate_scheduler_available()
    try:
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append(JobInfo(
                id=job.id,
                name=job.name,
                next_run=job.next_run_time.isoformat() if job.next_run_time else None,
                trigger=str(job.trigger),
            ))
        logger.info("Listed %d scheduled jobs", len(jobs))
        return JobListResponse(jobs=jobs)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to list jobs: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {exc}")


@router.post("/jobs/{task_key}/run", response_model=JobResult)
async def trigger_job(task_key: str):
    """Manually trigger a task execution immediately."""
    _validate_scheduler_available()
    task_def = get_task(task_key)
    if not task_def:
        log_job_operation("trigger", task_key, success=False, detail="Task not found")
        raise HTTPException(status_code=404, detail=f"Task not found: {task_key}")

    try:
        result = await task_def.func()
        log_job_operation("trigger", task_key, success=True)
        return JobResult(
            success=True,
            message=f"Task {task_key} executed successfully",
            task_key=task_key,
        )
    except HTTPException:
        raise
    except Exception as exc:
        log_job_operation("trigger", task_key, success=False, detail=str(exc))
        logger.error("Task execution failed for %s: %s", task_key, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Task execution failed: {exc}")


@router.post("/jobs/{task_key}/pause", response_model=JobResult)
async def pause_job(task_key: str):
    """Pause a scheduled job."""
    _validate_scheduler_available()
    try:
        scheduler.pause_job(task_key)
        log_job_operation("pause", task_key, success=True)
        return JobResult(success=True, message=f"Job {task_key} paused", task_key=task_key)
    except HTTPException:
        raise
    except Exception as exc:
        log_job_operation("pause", task_key, success=False, detail=str(exc))
        logger.error("Failed to pause job %s: %s", task_key, exc, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/jobs/{task_key}/resume", response_model=JobResult)
async def resume_job(task_key: str):
    """Resume a paused job."""
    _validate_scheduler_available()
    try:
        main_scheduler.resume_job(task_key)
        log_job_operation("resume", task_key, success=True)
        return JobResult(success=True, message=f"Job {task_key} resumed", task_key=task_key)
    except HTTPException:
        raise
    except Exception as exc:
        log_job_operation("resume", task_key, success=False, detail=str(exc))
        logger.error("Failed to resume job %s: %s", task_key, exc, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/jobs/{task_key}/reschedule", response_model=JobResult)
async def reschedule_job(task_key: str, payload: RescheduleRequest):
    """Change the cron schedule for a job."""
    _validate_scheduler_available()
    task_def = get_task(task_key)
    if not task_def:
        log_job_operation("reschedule", task_key, success=False, detail="Task not found")
        raise HTTPException(status_code=404, detail=f"Task not found: {task_key}")

    try:
        main_scheduler.reschedule_job(task_key, trigger="cron", cron=payload.cron)
        log_job_operation("reschedule", task_key, success=True, detail=f"new_cron={payload.cron}")
        return JobResult(
            success=True,
            message=f"Job {task_key} rescheduled to {payload.cron}",
            task_key=task_key,
        )
    except HTTPException:
        raise
    except Exception as exc:
        log_job_operation("reschedule", task_key, success=False, detail=str(exc))
        logger.error("Failed to reschedule job %s: %s", task_key, exc, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))
