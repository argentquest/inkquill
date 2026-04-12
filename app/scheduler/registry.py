"""Task registry for the scheduler server."""

from __future__ import annotations
import logging
from typing import Callable, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TaskDefinition:
    """Metadata for a schedulable task."""
    key: str
    name: str
    func: Callable
    default_cron: str
    description: str = ""
    enabled_by_default: bool = True
    max_instances: int = 1
    misfire_grace_time: int = 300


# Global registry
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
    """Decorator to register a function as a schedulable task."""
    def decorator(func: Callable) -> Callable:
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
        logger.info(f"Registered task: {key} ({name})")
        return func
    return decorator


def get_task(key: str) -> Optional[TaskDefinition]:
    """Look up a task by key."""
    return _TASKS.get(key)


def list_tasks() -> list[TaskDefinition]:
    """Return all registered tasks."""
    return list(_TASKS.values())
