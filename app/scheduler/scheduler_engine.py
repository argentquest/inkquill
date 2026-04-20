"""APScheduler engine with PostgreSQL-backed job persistence."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.core.config import settings


def build_job_store_url() -> str:
    """Build a synchronous psycopg2 URL for APScheduler's job store."""
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    job_store = SQLAlchemyJobStore(
        url=build_job_store_url(),
        tablename="scheduled_jobs"
    )

    executors = {
        "default": AsyncIOExecutor(),
    }

    job_defaults = {
        "coalesce": True,
        "max_instances": 1,
        "misfire_grace_time": settings.SCHEDULER_MISFIRE_GRACE_TIME,
    }

    scheduler = AsyncIOScheduler(
        jobstores={"default": job_store},
        executors=executors,
        job_defaults=job_defaults,
        timezone=settings.TIMEZONE,
    )

    return scheduler
