# /ai_rag_story_app/app/crud/location.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Optional, Any, Dict
import logging
from fastapi import BackgroundTasks

from app.models.location import Location, story_location_association_table
from app.models.uploaded_document import SourceElementTypeEnum
from app.schemas.location import LocationCreate, LocationUpdate
from app.crud import document as crud_document_db

logger = logging.getLogger(__name__)

async def create_location(db: AsyncSession, location_in: LocationCreate, world_id: int, user_id: int, background_tasks: BackgroundTasks, model_config_id: Optional[int] = None) -> Location:
    from app.processing.world_element_processor import generate_and_index_world_element_rag_text_task
    db_location = Location(**location_in.model_dump(), world_id=world_id)
    db.add(db_location)
    await db.flush()
    await db.refresh(db_location)
    background_tasks.add_task(
        generate_and_index_world_element_rag_text_task,
        element_type_str="location",
        element_id=db_location.id,
        user_id=user_id,
        world_id=db_location.world_id,
        background_tasks=background_tasks,
        model_config_id=model_config_id
    )
    return db_location

async def get_location(db: AsyncSession, location_id: int) -> Optional[Location]:
    result = await db.execute(select(Location).filter(Location.id == location_id).options(selectinload(Location.world), selectinload(Location.current_image)))
    return result.scalars().first()

async def get_locations_by_world(db: AsyncSession, world_id: int, skip: int = 0, limit: int = 100) -> List[Location]:
    result = await db.execute(
        select(Location).filter(Location.world_id == world_id).order_by(Location.name).offset(skip).limit(limit).options(selectinload(Location.current_image))
    )
    return result.scalars().all()

async def update_location(db: AsyncSession, db_location: Location, location_in: LocationUpdate, user_id: int, background_tasks: BackgroundTasks, model_config_id: Optional[int] = None) -> Location:
    from app.processing.world_element_processor import generate_and_index_world_element_rag_text_task
    update_data = location_in.model_dump(exclude_unset=True)
    significant_change = False
    if update_data:
        for key, value in update_data.items():
            if hasattr(db_location, key) and getattr(db_location, key) != value:
                setattr(db_location, key, value)
                if key in ['name', 'description', 'atmosphere', 'significance', 'image_prompt_definition']:
                    significant_change = True
    db.add(db_location)
    await db.flush()
    await db.refresh(db_location)
    if significant_change:
        background_tasks.add_task(
            generate_and_index_world_element_rag_text_task,
            element_type_str="location",
            element_id=db_location.id,
            user_id=user_id,
            world_id=db_location.world_id,
            background_tasks=background_tasks,
            model_config_id=model_config_id
        )
    return db_location

async def delete_location(db: AsyncSession, db_location: Location, user_id: int, world_id: int, background_tasks: BackgroundTasks) -> Location:
    from app.services.azure_ai_search_service import delete_documents_by_filter_from_index
    location_id_to_delete = db_location.id
    search_filter = f"source_element_id eq '{location_id_to_delete}' and element_type eq '{SourceElementTypeEnum.LOCATION_LORE.value}'"
    background_tasks.add_task(delete_documents_by_filter_from_index, filter_string=search_filter)
    await crud_document_db.delete_generated_document_records(db, SourceElementTypeEnum.LOCATION_LORE, location_id_to_delete, world_id, user_id, background_tasks)
    await db.delete(db_location)
    await db.flush()
    return db_location

async def link_location_to_story(db: AsyncSession,story_id: int,location_id: int,significance_to_story: Optional[str] = None) -> bool:
    try:
        values_to_set = {"story_id":story_id,"location_id":location_id,"significance_to_story":significance_to_story}
        stmt = pg_insert(story_location_association_table).values(**values_to_set)
        stmt = stmt.on_conflict_do_update(index_elements=['story_id','location_id'],set_=dict(significance_to_story=stmt.excluded.significance_to_story))
        await db.execute(stmt)
        await db.flush()
        return True
    except Exception as e:
        logger.error(f"Error linking location ID {location_id} to story ID {story_id}: {e}")
        return False

async def unlink_location_from_story(db: AsyncSession, story_id: int, location_id: int) -> bool:
    try:
        stmt = story_location_association_table.delete().where(story_location_association_table.c.story_id == story_id, story_location_association_table.c.location_id == location_id)
        result = await db.execute(stmt)
        await db.flush()
        return result.rowcount > 0
    except Exception as e:
        logger.error(f"Error unlinking location ID {location_id} from story ID {story_id}: {e}")
        return False

async def get_locations_for_story(db: AsyncSession, story_id: int) -> List[Dict[str, Any]]:
    query = (select(Location, story_location_association_table.c.significance_to_story)
        .join(story_location_association_table, Location.id == story_location_association_table.c.location_id)
        .options(selectinload(Location.current_image))
        .filter(story_location_association_table.c.story_id == story_id).order_by(Location.name))
    result = await db.execute(query)
    
    return [
        {"location": loc, "significance_to_story": sig}
        for loc, sig in result.all()
    ]

async def get_location_link_details(db: AsyncSession, story_id: int, location_id: int) -> Optional[dict]:
    query = (select(Location, story_location_association_table.c.significance_to_story).join(story_location_association_table, Location.id == story_location_association_table.c.location_id).filter(story_location_association_table.c.story_id == story_id, story_location_association_table.c.location_id == location_id))
    row = (await db.execute(query)).first()
    if row: loc, sig = row; return {"story_id":story_id,"location_id":loc.id,"significance_to_story":sig,"location":loc}
    return None

# --- Advanced World-Building Helper Functions ---

async def get_location_hierarchy_for_world(db: AsyncSession, world_id: int) -> List[Location]:
    """Get all locations in a world ordered by hierarchy (parents before children)."""
    result = await db.execute(
        select(Location)
        .filter(Location.world_id == world_id)
        .options(
            selectinload(Location.parent_location),
            selectinload(Location.child_locations)
        )
        .order_by(Location.parent_location_id.nulls_first(), Location.name)
    )
    return result.scalars().all()

async def get_child_locations(db: AsyncSession, parent_location_id: int) -> List[Location]:
    """Get all direct child locations of a parent location."""
    result = await db.execute(
        select(Location)
        .filter(Location.parent_location_id == parent_location_id)
        .order_by(Location.name)
    )
    return result.scalars().all()

async def get_root_locations(db: AsyncSession, world_id: int) -> List[Location]:
    """Get all root locations (no parent) in a world."""
    result = await db.execute(
        select(Location)
        .filter(Location.world_id == world_id, Location.parent_location_id.is_(None))
        .order_by(Location.name)
    )
    return result.scalars().all()

async def get_locations_with_coordinates(db: AsyncSession, world_id: int) -> List[Location]:
    """Get all locations in a world that have map coordinates set."""
    result = await db.execute(
        select(Location)
        .filter(
            Location.world_id == world_id,
            Location.map_x.is_not(None),
            Location.map_y.is_not(None)
        )
        .order_by(Location.map_x, Location.map_y)
    )
    return result.scalars().all()

async def validate_location_hierarchy(db: AsyncSession, location_id: int, proposed_parent_id: Optional[int]) -> bool:
    """Validate that setting a parent doesn't create a circular hierarchy."""
    if proposed_parent_id is None:
        return True
    
    if location_id == proposed_parent_id:
        return False
    
    current_parent_id = proposed_parent_id
    visited = set()
    
    while current_parent_id is not None:
        if current_parent_id in visited:
            return False
        if current_parent_id == location_id:
            return False
        
        visited.add(current_parent_id)
        
        result = await db.execute(
            select(Location.parent_location_id)
            .filter(Location.id == current_parent_id)
        )
        row = result.first()
        current_parent_id = row[0] if row else None
    
    return True