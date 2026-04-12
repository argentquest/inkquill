"""Base task class for scheduler tasks."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseTask(ABC):
    """Abstract base class for scheduled tasks."""

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """Execute the task and return results."""
        ...

    async def __call__(self) -> Dict[str, Any]:
        """Make the task callable for the scheduler."""
        logger.info(f"Starting task: {self.__class__.__name__}")
        try:
            result = await self.execute()
            result["task_class"] = self.__class__.__name__
            result["completed_at"] = datetime.utcnow().isoformat()
            logger.info(f"Task completed: {self.__class__.__name__}")
            return result
        except Exception as exc:
            logger.error(f"Task failed: {self.__class__.__name__}: {exc}", exc_info=True)
            raise
