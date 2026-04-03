"""Core application helpers for importer tasks."""

# /story_app/app/core/importer_tasks.py

import asyncio
import logging
from typing import Any, List, Callable, Coroutine

logger = logging.getLogger(__name__)

DB_TASK_SEMAPHORE = asyncio.Semaphore(5)

class ImporterBackgroundTasks:
    """Class for importer background tasks."""
    def __init__(self):
        self._tasks_to_run: List[Coroutine] = []
        logger.info("ImporterBackgroundTasks instance created.")

    def add_task(self, func: Callable, *args, **kwargs) -> None:
        """
        Wraps the given async function in a semaphore-controlled coroutine
        and collects it for later execution.
        """
        logger.info("ImporterBackgroundTasks: Collecting task '%s'...", func.__name__)

        async def semaphored_task():
            async with DB_TASK_SEMAPHORE:
                logger.info(
                    "Semaphore acquired for importer task: %s for element ID %s",
                    func.__name__,
                    args[1] if len(args) > 1 else "N/A",
                )
                await func(*args, **kwargs)
                logger.info(
                    "Semaphore released for importer task: %s for element ID %s",
                    func.__name__,
                    args[1] if len(args) > 1 else "N/A",
                )

        self._tasks_to_run.append(semaphored_task())

    async def execute_collected_tasks(self):
        """
        Executes all collected importer tasks concurrently, respecting the semaphore limit.
        """
        if self._tasks_to_run:
            num_tasks = len(self._tasks_to_run)
            logger.info(f"ImporterBackgroundTasks: Executing {num_tasks} tasks with concurrency limit of {DB_TASK_SEMAPHORE._value}.")
            try:
                await asyncio.gather(*self._tasks_to_run)
                logger.info(f"ImporterBackgroundTasks: Successfully completed all {num_tasks} collected tasks.")
            except Exception as e_gather:
                logger.error(f"ImporterBackgroundTasks: Error during asyncio.gather for importer tasks: {e_gather}", exc_info=True)
                raise
            finally:
                self._tasks_to_run = []
        else:
            logger.info("ImporterBackgroundTasks: No tasks were collected for execution.")

