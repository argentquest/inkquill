"""Pydantic schemas for the scheduler server API."""

from pydantic import BaseModel
from typing import List, Optional


class HealthResponse(BaseModel):
    status: str
    scheduler_running: bool
    registered_tasks: int
    scheduled_jobs: int


class TaskStatus(BaseModel):
    key: str
    name: str
    cron: str
    next_run: Optional[str] = None
    is_running: bool = False


class StatusResponse(BaseModel):
    tasks: List[TaskStatus]


class JobInfo(BaseModel):
    id: str
    name: str
    next_run: Optional[str] = None
    trigger: str


class JobListResponse(BaseModel):
    jobs: List[JobInfo]


class JobResult(BaseModel):
    success: bool
    message: str
    task_key: str


class RescheduleRequest(BaseModel):
    cron: str
