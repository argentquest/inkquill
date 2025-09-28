# /mnt/c/Code2025/rag/app/crud/chat_sample.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import logging

from app.models.chat_sample import ChatSample

logger = logging.getLogger(__name__)


async def get_active_chat_samples(db: AsyncSession) -> List[ChatSample]:
    """
    Get all active chat samples ordered by sort_order
    """
    logger.debug("CRUD: Fetching active chat samples")
    result = await db.execute(
        select(ChatSample)
        .where(ChatSample.is_active == True)
        .order_by(ChatSample.sort_order)
    )
    return result.scalars().all()


async def get_chat_sample_by_id(db: AsyncSession, sample_id: int) -> ChatSample:
    """
    Get a single chat sample by ID
    """
    logger.debug(f"CRUD: Fetching chat sample with ID: {sample_id}")
    return await db.get(ChatSample, sample_id)