"""APScheduler engine factory.

Design decisions
----------------
* AsyncIOScheduler — matches the FastAPI async event loop; tasks are plain
  async functions and must not block the loop.
* SQLAlchemyJobStore (psycopg2, *synchronous* URL) — APScheduler's job store
  uses a synchronous SQLAlchemy connection internally, which is why the URL
  uses postgresql:// (psycopg2) rather than the postgresql+asyncpg:// URL used
  by the rest of the application.  The two connection pools are independent.
* coalesce=True — if the scheduler misses several fire times (e.g. after a
  restart), it fires the job only once instead of attempting to catch up.
  Combined with misfire_grace_time, this prevents burst execution after downtime.
* replace_existing=True (set per job in main.py) — ensures that a cron change
  in code takes effect on the next startup without manual database edits.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.core.config import settings


def build_job_store_url() -> str:
    """Return a synchronous psycopg2 connection URL for APScheduler's job store.

    APScheduler's SQLAlchemyJobStore does not support asyncpg, so we build a
    standard postgresql:// URL here even though the main app uses asyncpg.
    """
    return (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def create_scheduler() -> AsyncIOScheduler:
    """Create and return a fully configured AsyncIOScheduler.

    The scheduler is *not* started here — call scheduler.start() inside the
    FastAPI lifespan so that startup and shutdown are tied to the app lifecycle.
    """
    job_store = SQLAlchemyJobStore(
        url=build_job_store_url(),
        # Separate table from the application tables to keep schema concerns
        # isolated.  Alembic migrations do not manage this table.
        tablename="scheduled_jobs",
    )

    executors = {
        # AsyncIOExecutor runs coroutines directly on the event loop.
        # Do NOT use ProcessPoolExecutor or ThreadPoolExecutor here — tasks use
        # async database sessions that are not thread/process safe.
        "default": AsyncIOExecutor(),
    }

    job_defaults = {
        # Fire the job once after a gap, not once per missed interval.
        "coalesce": True,
        # Per-job overrides in main.py take precedence over this default.
        "max_instances": 1,
        "misfire_grace_time": settings.SCHEDULER_MISFIRE_GRACE_TIME,
    }

    return AsyncIOScheduler(
        jobstores={"default": job_store},
        executors=executors,
        job_defaults=job_defaults,
        timezone=settings.TIMEZONE,
    )
