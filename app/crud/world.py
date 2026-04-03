"""Database CRUD helpers for world."""

# /story_app/app/crud/world.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.models.world import World
from app.schemas.world import WorldCreate, WorldUpdate

logger = logging.getLogger(__name__)

async def create_world(db: AsyncSession, world_in: WorldCreate, user_id: int) -> World:
    """Create world."""
    logger.info(f"User ID {user_id} creating new world: '{world_in.name}'")
    db_world = World(**world_in.model_dump(), user_id=user_id)
    db.add(db_world)
    await db.flush()
    await db.refresh(db_world)
    await db.commit()  # Commit the transaction to persist the world
    logger.info(f"World '{db_world.name}' (ID: {db_world.id}) created and committed for user ID: {user_id}.")
    return db_world

async def get_world(db: AsyncSession, world_id: int) -> Optional[World]:
    """Return world."""
    logger.debug(f"Fetching world with ID: {world_id}")
    result = await db.execute(
        select(World).filter(World.id == world_id).options(selectinload(World.owner))
    )
    return result.scalars().first()

async def get_world_for_user(db: AsyncSession, world_id: int, user_id: int) -> Optional[World]:
    """Return world for user."""
    logger.debug(f"Fetching world ID: {world_id} for user ID: {user_id}")
    result = await db.execute(
        select(World).filter(World.id == world_id, World.user_id == user_id)
        .options(selectinload(World.owner))
    )
    return result.scalars().first()

async def get_worlds_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[World]:
    """Return worlds by user."""
    logger.debug(f"Fetching worlds for user ID: {user_id}, skip: {skip}, limit: {limit}")
    result = await db.execute(
        select(World).filter(World.user_id == user_id).order_by(World.name).offset(skip).limit(limit)
        .options(selectinload(World.owner))
    )
    return result.scalars().all()

async def update_world(db: AsyncSession, db_world: World, world_in: WorldUpdate) -> World:
    """Update world."""
    update_data = world_in.model_dump(exclude_unset=True)
    logger.info(f"Updating world ID: {db_world.id} with data: {update_data}")
    for key, value in update_data.items():
        if hasattr(db_world, key):
            setattr(db_world, key, value)
    db.add(db_world)
    await db.flush()
    await db.refresh(db_world)
    logger.info(f"World ID: {db_world.id} updated in session.")
    return db_world

async def delete_world(db: AsyncSession, db_world: World) -> World:
    """Delete world."""
    logger.info(f"Deleting world ID: {db_world.id}. Cascades will apply.")
    # This function expects a world object that is attached to the current session 'db'.
    await db.delete(db_world)
    await db.flush()
    logger.info(f"World ID: {db_world.id} marked for deletion in session.")
    return db_world

async def user_has_non_shadow_worlds(db: AsyncSession, user_id: int) -> bool:
    """Check if a user has any non-shadow worlds."""
    logger.debug(f"Checking if user ID: {user_id} has non-shadow worlds")
    result = await db.execute(
        select(World).filter(World.user_id == user_id, World.is_shadow == False).limit(1)
    )
    return result.scalars().first() is not None
