# /ai_rag_story_app/app/core/importer_tasks.py

import asyncio
import logging
from typing import Any, List, Callable, Coroutine

logger = logging.getLogger(__name__)

DB_TASK_SEMAPHORE = asyncio.Semaphore(5)

class ImporterBackgroundTasks:
    def __init__(self):
        self._tasks_to_run: List[Coroutine] = []
        logger.info("ImporterBackgroundTasks instance created.")

    def add_task(self, func: Callable, *args, **kwargs) -> None:
        """
        Wraps the given async function in a semaphore-controlled coroutine
        and collects it for later execution.
        """
        if func.__name__ == "generate_and_index_world_element_rag_text_task":
            # --- FIX: kwargs will now contain the 'db' session ---
            logger.info(f"ImporterBackgroundTasks: Collecting RAG task '{func.__name__}'...")
            
            async def semaphored_task():
                async with DB_TASK_SEMAPHORE:
                    logger.info(f"Semaphore acquired for RAG task: {func.__name__} for element ID {args[1] if len(args) > 1 else 'N/A'}")
                    # Pass all original args and kwargs to the function
                    await func(*args, **kwargs)
                    logger.info(f"Semaphore released for RAG task: {func.__name__} for element ID {args[1] if len(args) > 1 else 'N/A'}")

            self._tasks_to_run.append(semaphored_task())
        else:
            logger.warning(f"ImporterBackgroundTasks: Note - A non-RAG task '{func.__name__}' was added. It will not be executed by this instance.")

    async def execute_collected_tasks(self):
        """
        Executes all collected RAG generation tasks concurrently, respecting the semaphore limit.
        """
        if self._tasks_to_run:
            num_tasks = len(self._tasks_to_run)
            logger.info(f"ImporterBackgroundTasks: Executing {num_tasks} RAG tasks with concurrency limit of {DB_TASK_SEMAPHORE._value}.")
            try:
                await asyncio.gather(*self._tasks_to_run)
                logger.info(f"ImporterBackgroundTasks: Successfully completed all {num_tasks} collected RAG tasks.")
            except Exception as e_gather:
                logger.error(f"ImporterBackgroundTasks: Error during asyncio.gather for RAG tasks: {e_gather}", exc_info=True)
                raise
            finally:
                self._tasks_to_run = []
        else:
            logger.info("ImporterBackgroundTasks: No RAG tasks were collected for execution.")