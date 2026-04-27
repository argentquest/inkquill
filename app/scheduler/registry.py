"""Task registry — maps task keys to their definitions.

Usage
-----
Decorate a task function with @register_task to add it to the global registry.
The scheduler startup loop (main.py) iterates list_tasks() and schedules every
entry whose enabled_by_default is True.

    @register_task(
        key="my_service.my_task",
        name="My Task",
        default_cron="0 4 * * *",
        description="Does something at 4 AM.",
    )
    async def my_task() -> dict:
        ...

Task keys should follow the pattern  <service>.<action>  so the admin UI can
group and sort them sensibly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class TaskDefinition:
    """All metadata for a single schedulable task.

    Attributes
    ----------
    key:
        Unique identifier used as the APScheduler job ID and the URL path
        segment in the admin API (e.g. POST /scheduler/jobs/{key}/run).
    name:
        Human-readable label shown in the admin UI.
    func:
        The async (or sync) callable that APScheduler will invoke.
    default_cron:
        5-field cron expression used when first scheduling the job.  Can be
        overridden at runtime via the reschedule API without restarting.
    description:
        One-sentence explanation shown in the admin UI tooltip.
    enabled_by_default:
        If False the task is registered in the registry but NOT scheduled at
        startup.  Useful for dev-only or opt-in tasks.
    max_instances:
        Maximum concurrent executions APScheduler will allow for this job.
        Set > 1 only for tasks that are safe to run in parallel (e.g. fan-out
        over independent patients).
    misfire_grace_time:
        Seconds after the scheduled fire time within which a missed job is
        still considered eligible to run.  After this window APScheduler
        discards the missed fire.
    """

    key: str
    name: str
    func: Callable
    default_cron: str
    description: str = ""
    enabled_by_default: bool = True
    max_instances: int = 1
    misfire_grace_time: int = 300


# Module-level registry — populated at import time by @register_task calls.
# Access only through get_task() / list_tasks() so callers don't depend on
# the internal dict structure.
_TASKS: dict[str, TaskDefinition] = {}


def register_task(
    key: str,
    name: str,
    default_cron: str,
    description: str = "",
    enabled_by_default: bool = True,
    max_instances: int = 1,
    misfire_grace_time: int = 300,
) -> Callable:
    """Decorator factory — register a function as a schedulable task.

    Returns the original function unchanged so the decorated function can
    still be called directly (e.g. from tests or the precache startup warm).
    """
    def decorator(func: Callable) -> Callable:
        if key in _TASKS:
            logger.warning("Task key '%s' is already registered — overwriting.", key)
        _TASKS[key] = TaskDefinition(
            key=key,
            name=name,
            func=func,
            default_cron=default_cron,
            description=description,
            enabled_by_default=enabled_by_default,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
        )
        logger.debug("Registered task: %s (%s)", key, name)
        return func
    return decorator


def get_task(key: str) -> Optional[TaskDefinition]:
    """Return the TaskDefinition for *key*, or None if not registered."""
    return _TASKS.get(key)


def list_tasks() -> list[TaskDefinition]:
    """Return all registered tasks in insertion order."""
    return list(_TASKS.values())
