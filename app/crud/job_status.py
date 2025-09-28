# /ai_rag_story_app/app/crud/job_status.py

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.job_status import JobStatus, JobTypeEnum, JobStateEnum
from typing import Optional

logger = logging.getLogger(__name__)

async def create_job(db: AsyncSession, job_id: str, user_id: int, job_type: JobTypeEnum, status_message: str) -> JobStatus:
    db_job = JobStatus(
        job_id=job_id,
        user_id=user_id,
        job_type=job_type,
        state=JobStateEnum.PENDING,
        status_message=status_message
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job

async def get_job_by_job_id(db: AsyncSession, job_id: str, user_id: int) -> Optional[JobStatus]:
    result = await db.execute(
        select(JobStatus).filter(JobStatus.job_id == job_id, JobStatus.user_id == user_id)
    )
    return result.scalars().first()

async def update_job_status(db: AsyncSession, job_id: str, state: JobStateEnum, status_message: Optional[str] = None, result_message: Optional[str] = None, world_id: Optional[int] = None) -> Optional[JobStatus]:
    result = await db.execute(select(JobStatus).filter(JobStatus.job_id == job_id))
    db_job = result.scalars().first()

    if not db_job:
        logger.warning(f"Attempted to update status for non-existent job_id: {job_id}")
        return None
    
    db_job.state = state
    if status_message is not None:
        db_job.status_message = status_message
    if result_message is not None:
        db_job.result_message = result_message
    if world_id is not None:
        db_job.world_id = world_id
    
    await db.commit()
    await db.refresh(db_job)
    return db_job


async def create_job_status(
    db: AsyncSession,
    job_id: str,
    job_type: JobTypeEnum,
    user_id: int,
    world_id: Optional[int] = None,
    status_message: str = "Job created",
    result_message: Optional[str] = None
) -> JobStatus:
    """Create a new job status record"""
    db_job = JobStatus(
        job_id=job_id,
        job_type=job_type,
        user_id=user_id,
        world_id=world_id,
        state=JobStateEnum.PENDING,
        status_message=status_message,
        result_message=result_message
    )
    db.add(db_job)
    await db.flush()  # Don't commit, let caller handle it
    return db_job