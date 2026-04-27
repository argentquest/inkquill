"""Pydantic response / request schemas for the scheduler admin API.

All schemas are intentionally kept flat (no nested unions) so the Next.js
frontend can type them without complex discriminated-union handling.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class HealthResponse(BaseModel):
    """Returned by GET /scheduler/health."""

    status: str = Field(description="'healthy' or 'unhealthy'")
    scheduler_running: bool = Field(description="Whether APScheduler.running is True")
    registered_tasks: int = Field(description="Tasks registered via @register_task")
    scheduled_jobs: int = Field(description="Jobs currently loaded in APScheduler")


class TaskStatus(BaseModel):
    """One entry in the StatusResponse.tasks list.

    Combines the static task definition (from the registry) with the live
    APScheduler job state so the frontend can show both in a single card.
    """

    key: str = Field(description="Unique task identifier, e.g. 'care_circle.daily_newsletter'")
    name: str = Field(description="Human-readable display name")
    cron: str = Field(description="Default cron expression from the registry")
    next_run: Optional[str] = Field(None, description="ISO-8601 next run time, or null if paused/missing")
    is_running: bool = Field(False, description="True if APScheduler has an active job for this key")


class StatusResponse(BaseModel):
    """Returned by GET /scheduler/status."""

    tasks: List[TaskStatus]


class JobInfo(BaseModel):
    """One row in the JobListResponse.jobs list.

    Represents a concrete APScheduler job, independent of the registry.
    Use this to inspect jobs that may have been rescheduled away from their
    default cron.
    """

    id: str = Field(description="APScheduler job ID (matches the task key)")
    name: str = Field(description="APScheduler job name")
    next_run: Optional[str] = Field(None, description="ISO-8601 next run time")
    trigger: str = Field(description="str(job.trigger) as returned by APScheduler")


class JobListResponse(BaseModel):
    """Returned by GET /scheduler/jobs."""

    jobs: List[JobInfo]


class JobResult(BaseModel):
    """Returned by all POST /scheduler/jobs/{task_key}/* mutation endpoints."""

    success: bool
    message: str
    task_key: str


class RescheduleRequest(BaseModel):
    """Request body for POST /scheduler/jobs/{task_key}/reschedule."""

    cron: str = Field(
        description=(
            "Standard 5-field cron expression (minute hour day month weekday). "
            "Validated by APScheduler's CronTrigger.from_crontab()."
        )
    )
