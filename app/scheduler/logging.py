"""Structured logging utilities for the scheduler server."""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@asynccontextmanager
async def task_execution_context(task_key: str, task_name: str):
    """Context manager for structured task execution logging.

    Provides:
    - Timing information
    - Structured start/complete/error log entries
    - Result tracking
    """
    start_time = time.monotonic()
    start_ts = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Task execution started",
        extra={
            "task_key": task_key,
            "task_name": task_name,
            "event": "task_start",
            "timestamp": start_ts,
        }
    )

    result: Dict[str, Any] = {
        "task_key": task_key,
        "started_at": start_ts,
    }

    try:
        yield result
        elapsed = time.monotonic() - start_time
        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        result["duration_seconds"] = round(elapsed, 3)
        result["status"] = "success"

        logger.info(
            "Task execution completed",
            extra={
                "task_key": task_key,
                "task_name": task_name,
                "event": "task_complete",
                "duration_seconds": result["duration_seconds"],
                "status": "success",
            }
        )
    except Exception as exc:
        elapsed = time.monotonic() - start_time
        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        result["duration_seconds"] = round(elapsed, 3)
        result["status"] = "error"
        result["error"] = str(exc)

        logger.error(
            "Task execution failed",
            extra={
                "task_key": task_key,
                "task_name": task_name,
                "event": "task_error",
                "duration_seconds": result["duration_seconds"],
                "error": str(exc),
                "error_type": type(exc).__name__,
            },
            exc_info=True,
        )
        raise


def log_job_operation(operation: str, task_key: str, success: bool, detail: str = ""):
    """Log a job management operation (pause, resume, trigger, reschedule)."""
    log_func = logger.info if success else logger.warning
    log_func(
        f"Job operation: {operation}",
        extra={
            "operation": operation,
            "task_key": task_key,
            "success": success,
            "detail": detail,
        }
    )


def log_scheduler_event(event: str, detail: str = "", level: str = "info"):
    """Log a scheduler-level event (startup, shutdown, error)."""
    log_func = getattr(logger, level, logger.info)
    log_func(
        f"Scheduler event: {event}",
        extra={
            "event": event,
            "detail": detail,
        }
    )
