"""Database CRUD helpers for lore item."""

# /story_app/app/crud/lore_item.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Optional, Any, Dict
import logging
from fastapi import BackgroundTasks

from app.models.lore_item import LoreItem, LoreItemCategoryEnum, story_lore_item_association_table
from app.models.uploaded_document import SourceElementTypeEnum
from app.schemas.lore_item import LoreItemCreate, LoreItemUpdate
from app.crud import document as crud_document_db

logger = logging.getLogger(__name__)

async def create_lore_item(db: AsyncSession, lore_item_in: LoreItemCreate, world_id: int, user_id: int, background_tasks: BackgroundTasks, model_config_id: Optional[int] = None) -> LoreItem:
    """Create lore item."""
    db_lore_item = LoreItem(**lore_item_in.model_dump(), world_id=world_id)
    db.add(db_lore_item)
    await db.flush()
    await db.refresh(db_lore_item)
    return db_lore_item

async def get_lore_item(db: AsyncSession, lore_item_id: int) -> Optional[LoreItem]:
    """Return lore item."""
    result = await db.execute(select(LoreItem).filter(LoreItem.id == lore_item_id).options(selectinload(LoreItem.world), selectinload(LoreItem.current_image)))
    return result.scalars().first()

async def get_lore_items_by_world(
    db: AsyncSession, world_id: int, category: Optional[LoreItemCategoryEnum] = None, skip: int = 0, limit: int = 100
) -> List[LoreItem]:
    """Return lore items by world."""
    query = select(LoreItem).filter(LoreItem.world_id == world_id).options(selectinload(LoreItem.current_image))
    if category:
        query = query.filter(LoreItem.category == category)
    query = query.order_by(LoreItem.title).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_lore_item(db: AsyncSession, db_lore_item: LoreItem, lore_item_in: LoreItemUpdate, user_id: int, background_tasks: BackgroundTasks, model_config_id: Optional[int] = None) -> LoreItem:
    """Update lore item."""
    update_data = lore_item_in.model_dump(exclude_unset=True)
    significant_change = False
    if update_data:
        for key, value in update_data.items():
            if hasattr(db_lore_item, key) and getattr(db_lore_item, key) != value:
                setattr(db_lore_item, key, value)
                if key in ['title', 'description', 'category', 'image_prompt_definition']:
                    significant_change = True
    db.add(db_lore_item)
    await db.flush()
    await db.refresh(db_lore_item)
    if significant_change:
        logger.info("Significant narrative fields changed for lore item ID %s.", db_lore_item.id)
    return db_lore_item

async def delete_lore_item(db: AsyncSession, db_lore_item: LoreItem, user_id: int, world_id: int, background_tasks: BackgroundTasks) -> LoreItem:
    """Delete lore item."""
    lore_item_id_to_delete = db_lore_item.id
    await crud_document_db.delete_generated_document_records(db, SourceElementTypeEnum.LORE_ITEM_LORE, lore_item_id_to_delete, world_id, user_id, background_tasks)
    await db.delete(db_lore_item)
    await db.flush()
    return db_lore_item

async def link_lore_item_to_story(db: AsyncSession,story_id: int,lore_item_id: int,relevance_to_story: Optional[str] = None) -> bool:
    """Perform database work for link lore item to story."""
    try:
        values_to_set = {"story_id":story_id,"lore_item_id":lore_item_id,"relevance_to_story":relevance_to_story}
        stmt = pg_insert(story_lore_item_association_table).values(**values_to_set)
        stmt = stmt.on_conflict_do_update(index_elements=['story_id','lore_item_id'],set_=dict(relevance_to_story=stmt.excluded.relevance_to_story))
        await db.execute(stmt)
        await db.flush()
        return True
    except Exception as e:
        logger.error(f"Error linking lore item ID {lore_item_id} to story ID {story_id}: {e}")
        return False

async def unlink_lore_item_from_story(db: AsyncSession, story_id: int, lore_item_id: int) -> bool:
    """Perform database work for unlink lore item from story."""
    try:
        stmt = story_lore_item_association_table.delete().where(story_lore_item_association_table.c.story_id == story_id, story_lore_item_association_table.c.lore_item_id == lore_item_id)
        result = await db.execute(stmt)
        await db.flush()
        return result.rowcount > 0
    except Exception as e:
        logger.error(f"Error unlinking lore item ID {lore_item_id} from story ID {story_id}: {e}")
        return False

async def get_lore_items_for_story(db: AsyncSession, story_id: int) -> List[Dict[str, Any]]:
    """Return lore items for story."""
    query = (select(LoreItem, story_lore_item_association_table.c.relevance_to_story)
             .join(story_lore_item_association_table, LoreItem.id == story_lore_item_association_table.c.lore_item_id)
             .options(selectinload(LoreItem.current_location), selectinload(LoreItem.current_image))
             .filter(story_lore_item_association_table.c.story_id == story_id)
             .order_by(LoreItem.title))
    result = await db.execute(query)
    
    return [
        {"lore_item": item, "relevance_to_story": rel}
        for item, rel in result.all()
    ]

async def get_lore_item_link_details(db: AsyncSession, story_id: int, lore_item_id: int) -> Optional[dict]:
    """Return lore item link details."""
    query = (select(LoreItem, story_lore_item_association_table.c.relevance_to_story).join(story_lore_item_association_table, LoreItem.id == story_lore_item_association_table.c.lore_item_id).filter(story_lore_item_association_table.c.story_id == story_id, story_lore_item_association_table.c.lore_item_id == lore_item_id))
    row = (await db.execute(query)).first()
    if row: item, rel = row; return {"story_id":story_id,"lore_item_id":item.id,"relevance_to_story":rel,"lore_item":item}
    return None

