"""Scheduler Server — FastAPI entry point.

This process runs independently from the main backend (app/main.py).  It owns
all background jobs (newsletter dispatch, session pre-generation, provider
pre-caching, cleanup) and exposes a small admin API used by the Next.js
frontend at /api/admin/scheduler/*.

Architecture notes
------------------
* APScheduler (AsyncIO) persists job state to the shared PostgreSQL database
  so scheduled run times survive process restarts.
* Tasks are registered at import time via the @register_task decorator; the
  lifespan function imports every task module to trigger registration, then
  schedules the enabled ones.
* The admin UI that previously lived here as a static HTML bundle was replaced
  by the Next.js component at
  frontendv1/components/care-circle-family/scheduler-admin-console.tsx.
  The static-file serving code has been removed — do not re-add it.

Environment variables (from root .env)
---------------------------------------
SCHEDULER_HOST — bind address (default 127.0.0.1; use 0.0.0.0 for Docker/server)
SCHEDULER_PORT — listen port (default 8001)
LOG_LEVEL_CONSOLE / LOG_LEVEL_FILE / APP_LOG_DIR — logging configuration
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

# asyncpg is incompatible with Windows ProactorEventLoop (the default on Python
# 3.8+ on Windows). Switching to SelectorEventLoop prevents the spurious
# "InvalidStateError: invalid state" crash on shutdown.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings, log_application_settings
from app.core.logging_config import setup_logging
from app.scheduler.scheduler_engine import create_scheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging before anything else so that task-module imports are
# captured in the scheduler's own log file (logs/app_scheduler.log).
setup_logging(
    log_level_console_str=os.getenv("LOG_LEVEL_CONSOLE", "INFO"),
    log_level_file_str=os.getenv("LOG_LEVEL_FILE", "DEBUG"),
    clear_existing_handlers=os.getenv("CLEAR_LOG_HANDLERS", "true").lower() == "true",
    log_filename_base="app_scheduler",
)

logger = logging.getLogger(__name__)

# Module-level reference kept so the /scheduler/health endpoint can inspect it
# via request.app.state.scheduler without importing from here directly.
scheduler = None


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Start the scheduler on startup; shut it down cleanly on exit."""
    global scheduler

    logger.info("Scheduler Server: Starting up...")
    log_application_settings()

    scheduler = create_scheduler()
    app_instance.state.scheduler = scheduler

    # Importing each task module triggers its @register_task decorator,
    # populating the global registry before we iterate over it below.
    from app.scheduler.tasks import (  # noqa: F401
        care_circle_newsletter,
        care_circle_newsletter_pdf,
        care_circle_session,
        care_circle_precache,
        care_circle_mini_newsletter,
        cleanup,
        diagnostic,
    )

    from app.scheduler.registry import list_tasks
    for task_def in list_tasks():
        if task_def.enabled_by_default:
            scheduler.add_job(
                func=task_def.func,
                trigger=CronTrigger.from_crontab(task_def.default_cron),
                id=task_def.key,
                name=task_def.name,
                max_instances=task_def.max_instances,
                misfire_grace_time=task_def.misfire_grace_time,
                # replace_existing ensures a code-level cron change takes
                # effect on the next startup without manual DB surgery.
                replace_existing=True,
            )
            logger.info("Scheduled task: %s  cron=%s", task_def.key, task_def.default_cron)

    scheduler.start()
    logger.info("Scheduler Server: Started — %d tasks scheduled", len(list_tasks()))

    # Kick off a cache warm immediately so today + the next few days are
    # covered before the nightly 2 AM job would normally run.
    from app.scheduler.tasks.care_circle_precache import precache_provider_outputs
    asyncio.create_task(precache_provider_outputs())

    try:
        yield
    finally:
        logger.info("Scheduler Server: Shutting down...")
        if scheduler:
            # wait=False avoids blocking the event loop during SIGTERM handling.
            scheduler.shutdown(wait=False)
        app_instance.state.scheduler = None
        logger.info("Scheduler Server: Shutdown complete")


app = FastAPI(
    title="Ink & Quill Scheduler",
    description=(
        "Background task scheduler for Care Circle and platform services. "
        "Admin endpoints are proxied through the Next.js frontend at "
        "/api/admin/scheduler/*."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS is configured so that direct API calls from the Next.js dev server
# (port 3001) work during local development.  In production all scheduler
# traffic arrives via the Next.js server-side proxy, not the browser directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o).strip() for o in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers are imported after app creation to avoid circular-import issues
# (routers import from registry which is populated during lifespan).
from app.scheduler.routers.health import router as health_router  # noqa: E402
from app.scheduler.routers.jobs import router as jobs_router  # noqa: E402

app.include_router(health_router, prefix="/scheduler", tags=["Health"])
app.include_router(jobs_router, prefix="/scheduler", tags=["Jobs"])


if __name__ == "__main__":
    import uvicorn

    # SCHEDULER_HOST and SCHEDULER_PORT are set in the root .env.
    # Use SCHEDULER_HOST=0.0.0.0 when the process must accept connections
    # from Docker containers (e.g. the frontend container via host.docker.internal).
    host = os.getenv("SCHEDULER_HOST", settings.SCHEDULER_HOST)
    port = settings.SCHEDULER_PORT
    uvicorn.run("app.scheduler.main:app", host=host, port=port, reload=False, log_level="info")
