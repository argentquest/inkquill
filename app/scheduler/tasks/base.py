"""Abstract base class for scheduler tasks.

NOTE — this class is not currently used.  All tasks in this project are
registered as plain async functions via the @register_task decorator, which is
simpler and works well with APScheduler's function-based job API.

BaseTask is preserved here as an opt-in alternative for teams that prefer a
class-based structure.  To use it:

    class MyTask(BaseTask):
        async def execute(self) -> dict:
            ...

    instance = MyTask()
    scheduler.add_job(instance, ...)  # APScheduler calls instance.__call__()
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseTask(ABC):
    """Abstract base for scheduled tasks that prefer a class-based structure.

    Subclasses implement execute(); the __call__ wrapper handles logging and
    error propagation so individual tasks stay focused on their business logic.
    """

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """Perform the task work and return a result dict."""
        ...

    async def __call__(self) -> Dict[str, Any]:
        """Entry point called by APScheduler.  Wraps execute() with logging."""
        logger.info("Starting task: %s", self.__class__.__name__)
        try:
            result = await self.execute()
            result["task_class"] = self.__class__.__name__
            result["completed_at"] = datetime.now(timezone.utc).isoformat()
            logger.info("Task completed: %s", self.__class__.__name__)
            return result
        except Exception as exc:
            logger.error("Task failed: %s: %s", self.__class__.__name__, exc, exc_info=True)
            raise
