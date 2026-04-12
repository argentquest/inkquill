"""FastAPI Scheduler Server entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, log_application_settings
from app.scheduler.scheduler_engine import create_scheduler
from app.scheduler.routers.health import router as health_router
from app.scheduler.routers.jobs import router as jobs_router

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Manage scheduler lifecycle."""
    global scheduler

    logger.info("Scheduler Server: Starting up...")
    log_application_settings()

    # Create and start scheduler
    scheduler = create_scheduler()

    # Register all tasks from the tasks package
    from app.scheduler.tasks import care_circle_newsletter, care_circle_session, cleanup  # noqa: F401

    # Schedule enabled tasks
    from app.scheduler.registry import list_tasks
    for task_def in list_tasks():
        if task_def.enabled_by_default:
            scheduler.add_job(
                func=task_def.func,
                trigger="cron",
                id=task_def.key,
                name=task_def.name,
                cron=task_def.default_cron,
                max_instances=task_def.max_instances,
                misfire_grace_time=task_def.misfire_grace_time,
                replace_existing=True,
            )
            logger.info(f"Scheduled task: {task_def.key} ({task_def.default_cron})")

    scheduler.start()
    logger.info("Scheduler Server: Started")

    try:
        yield
    finally:
        logger.info("Scheduler Server: Shutting down...")
        if scheduler:
            scheduler.shutdown(wait=False)
        logger.info("Scheduler Server: Shutdown complete")


app = FastAPI(
    title="Ink & Quill Scheduler",
    description="Background task scheduler for Care Circle and platform services",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend access to health/status
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o).strip() for o in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the management UI
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_ui():
    """Serve the scheduler management UI."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Scheduler UI not found. Build the static files first."}


# Include routers
app.include_router(health_router, prefix="/scheduler", tags=["Health"])
app.include_router(jobs_router, prefix="/scheduler", tags=["Jobs"])


if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = int(getattr(settings, "SCHEDULER_PORT", 8001))
    uvicorn.run(
        "app.scheduler.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )
