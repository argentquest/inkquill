# /ai_rag_story_app/app/crud/generated_image.py
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.generated_image import GeneratedImage

logger = logging.getLogger(__name__)

async def get_image(db: AsyncSession, image_id: int) -> Optional[GeneratedImage]:
    """
    Retrieves a single GeneratedImage by its ID.
    """
    return await db.get(GeneratedImage, image_id)

async def get_images_for_element(
    db: AsyncSession, *, element_type: str, element_id: int, skip: int = 0, limit: int = 100
) -> List[GeneratedImage]:
    """
    Retrieves a list of all generated images for a specific element,
    ordered by creation date (newest first).
    """
    stmt = (
        select(GeneratedImage)
        .filter(GeneratedImage.element_type == element_type)
        .filter(GeneratedImage.associated_element_id == element_id)
        .order_by(GeneratedImage.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()