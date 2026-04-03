"""Background processing helpers for world element processor."""

import logging
from typing import Optional

from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)


async def generate_world_element_context_task(
    element_type_str: str,
    element_id: int,
    user_id: int,
    world_id: int,
    background_tasks: BackgroundTasks,
    model_config_id: Optional[int] = None,
) -> None:
    """Generate world element context task."""
    logger.info(
        "Skipping background world-element context generation for %s %s in world %s; direct context is assembled at request time.",
        element_type_str,
        element_id,
        world_id,
    )
