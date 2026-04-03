"""Database CRUD helpers for character."""

# /story_app/app/crud/character.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import List, Optional, Any, Dict
import logging
from fastapi import BackgroundTasks

from app.models.character import Character, story_character_association_table
from app.models.story import Story 
from app.models.world import World 
from app.models.uploaded_document import SourceElementTypeEnum
from app.schemas.character import CharacterCreate, CharacterUpdate
from app.crud import document as crud_document_db

logger = logging.getLogger(__name__)

async def create_character(
    db: AsyncSession, 
    character_in: CharacterCreate, 
    world_id: int,
    user_id: int, 
    background_tasks: BackgroundTasks,
    model_config_id: Optional[int] = None
) -> Character:
    """Create character."""
    logger.info(f"User ID {user_id} creating new character '{character_in.name}' for world ID: {world_id}")
    logger.debug(f"Character data to be inserted: {character_in.model_dump()}")
    
    try:
        db_character = Character(**character_in.model_dump(), world_id=world_id)
        logger.debug(f"Character object created with attributes: name={db_character.name}, world_id={db_character.world_id}")
        
        db.add(db_character)
        logger.debug(f"Character added to session, attempting flush...")
        
        await db.flush() # Flush to get the ID without committing
        await db.refresh(db_character)
        logger.info(f"Character '{db_character.name}' (ID: {db_character.id}) flushed to DB for world ID: {world_id}.")
        
        # Commit the character to database before starting background task
        await db.commit()
        logger.info(f"Character '{db_character.name}' (ID: {db_character.id}) committed to database.")
        
        return db_character
    except Exception as e:
        logger.error(f"Error creating character '{character_in.name}' in world ID {world_id}: {e}", exc_info=True)
        logger.error(f"Character schema data that caused error: {character_in.model_dump()}")
        await db.rollback()
        raise

async def update_character(
    db: AsyncSession,
    db_character: Character,
    character_in: CharacterUpdate,
    user_id: int, 
    background_tasks: BackgroundTasks,
    model_config_id: Optional[int] = None
) -> Character:
    """Update character."""
    update_data = character_in.model_dump(exclude_unset=True)
    logger.info(f"User ID {user_id} updating character ID: {db_character.id} ('{db_character.name}') with data: {update_data}")
    
    if not update_data:
        logger.info(f"No update data provided for character ID: {db_character.id}.")
        return db_character

    significant_change = False
    for key, value in update_data.items():
        if hasattr(db_character, key):
            if getattr(db_character, key) != value:
                setattr(db_character, key, value)
                if key in ['name', 'description', 'personality_traits', 'backstory', 'image_prompt_definition',
                          'age_category', 'profession', 'core_motivations', 'short_backstory', 
                          'next_quest_scenario', 'first_meeting_message', 'visual_prompt']:
                    significant_change = True
            
    db.add(db_character)
    await db.flush()
    await db.refresh(db_character)
    logger.info(f"Character ID: {db_character.id} updated in DB session successfully.")

    if significant_change:
        logger.info(f"Significant narrative fields changed for character ID: {db_character.id}.")
            
    return db_character


async def get_character(db: AsyncSession, character_id: int) -> Optional[Character]:
    """Return character."""
    logger.debug(f"Fetching character with ID: {character_id}")
    result = await db.execute(
        select(Character)
        .filter(Character.id == character_id)
        .options(
            selectinload(Character.world),
            selectinload(Character.current_image)
        )
    )
    return result.scalars().first()

async def get_characters_by_world(db: AsyncSession, world_id: int, skip: int = 0, limit: int = 100) -> List[Character]:
    """Return characters by world."""
    logger.debug(f"Fetching characters for world ID: {world_id}, skip: {skip}, limit: {limit}")
    result = await db.execute(
        select(Character)
        .filter(Character.world_id == world_id)
        .order_by(Character.name)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Character.current_image))
    )
    return result.scalars().all()

async def delete_character(db: AsyncSession, db_character: Character, user_id: int, world_id: int, background_tasks: BackgroundTasks) -> Character:
    """Delete character."""
    character_id_to_delete = db_character.id
    logger.info(f"User ID {user_id} deleting character ID: {character_id_to_delete} ('{db_character.name}') from world ID {world_id}")
    await crud_document_db.delete_generated_document_records(db=db, source_element_type=SourceElementTypeEnum.CHARACTER_LORE, source_element_id=character_id_to_delete, world_id=world_id, user_id=user_id, background_tasks=background_tasks)
    await db.delete(db_character)
    await db.flush()
    return db_character

async def link_character_to_story(db: AsyncSession,story_id: int,character_id: int,role_in_story: Optional[str] = None) -> bool:
    """Perform database work for link character to story."""
    values_to_set = {"story_id": story_id, "character_id": character_id, "role_in_story": role_in_story}
    stmt = pg_insert(story_character_association_table).values(**values_to_set)
    stmt = stmt.on_conflict_do_update(index_elements=['story_id', 'character_id'], set_=dict(role_in_story=stmt.excluded.role_in_story))
    try: await db.execute(stmt); await db.commit(); return True
    except Exception as e: await db.rollback(); logger.error(f"Error linking/updating role charID {character_id} to storyID {story_id}: {e}"); return False

async def unlink_character_from_story(db: AsyncSession, story_id: int, character_id: int) -> bool:
    """Perform database work for unlink character from story."""
    stmt = story_character_association_table.delete().where(story_character_association_table.c.story_id == story_id, story_character_association_table.c.character_id == character_id)
    try: result = await db.execute(stmt); await db.commit(); return result.rowcount > 0
    except Exception as e: await db.rollback(); logger.error(f"Error unlinking charID {character_id} from storyID {story_id}: {e}"); return False

async def get_characters_for_story(db: AsyncSession, story_id: int) -> List[Dict[str, Any]]:
    """
    Fetches characters linked to a story, returning a list of dictionaries
    that include the ORM object and their role in the story.
    """
    query = (
        select(Character, story_character_association_table.c.role_in_story)
        .join(story_character_association_table, Character.id == story_character_association_table.c.character_id)
        .options(
            selectinload(Character.current_location),
            selectinload(Character.current_image)
        )
        .filter(story_character_association_table.c.story_id == story_id)
        .order_by(Character.name)
    )
    result = await db.execute(query)
    
    return [
        {"character": char_obj, "role_in_story": role}
        for char_obj, role in result.all()
    ]

async def get_character_link_details(db: AsyncSession, story_id: int, character_id: int) -> Optional[dict]:
    """Return character link details."""
    query = (select(Character, story_character_association_table.c.role_in_story).join(story_character_association_table, Character.id == story_character_association_table.c.character_id).filter(story_character_association_table.c.story_id == story_id, story_character_association_table.c.character_id == character_id))
    row = (await db.execute(query)).first()
    if row: c, role = row; return {"story_id":story_id,"character_id":c.id,"role_in_story":role,"character":c}
    return None

