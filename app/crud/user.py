# /ai_rag_story_app/app/crud/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.models import user as model_user
from app.schemas import user as schema_user
from app.core.security import get_password_hash

async def get_user(db: AsyncSession, user_id: int) -> Optional[model_user.User]:
    result = await db.execute(select(model_user.User).filter(model_user.User.id == user_id))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[model_user.User]:
    result = await db.execute(select(model_user.User).filter(model_user.User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[model_user.User]:
    result = await db.execute(select(model_user.User).filter(model_user.User.email == email))
    return result.scalars().first()

async def get_user_by_reset_token(db: AsyncSession, reset_token: str) -> Optional[model_user.User]:
    result = await db.execute(select(model_user.User).filter(model_user.User.reset_token == reset_token))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[model_user.User]:
    result = await db.execute(
        select(model_user.User).offset(skip).limit(limit).order_by(model_user.User.id)
    )
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schema_user.UserCreate) -> model_user.User:
    # Ensure hashed_password is never None since the database column is non-nullable
    if user.password:
        hashed_password = get_password_hash(user.password)
    else:
        # Generate a random password for users without one (like anonymous users)
        import secrets
        random_password = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(random_password)
    
    db_user = model_user.User(
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        hashed_password=hashed_password,
        is_active=True  # Ensure new users are active by default
    )
    db.add(db_user)
    # The commit is handled by the calling router function
    return db_user

async def update_user(db: AsyncSession, db_user: model_user.User, user_in: schema_user.UserUpdate) -> model_user.User:
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    elif "password" in update_data:
         del update_data["password"]

    for key, value in update_data.items():
        if hasattr(db_user, key):
             setattr(db_user, key, value)

    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int) -> Optional[model_user.User]:
    db_user = await get_user(db, user_id=user_id)
    if db_user:
        await db.delete(db_user)
        await db.flush()
    return db_user

# User Statistics Functions
async def get_user_statistics(db: AsyncSession, user_id: int) -> dict:
    """Get comprehensive user statistics"""
    from app.models.story import Story
    from app.models.world import World
    from app.models.character import Character
    from app.models.location import Location
    from app.models.lore_item import LoreItem
    from app.models.act import Act
    from app.models.scene import Scene
    from app.models.ai_cost_log import AICallLog
    from sqlalchemy import func, and_
    
    # Stories count
    stories_result = await db.execute(
        select(func.count(Story.id)).filter(Story.user_id == user_id)
    )
    stories_count = stories_result.scalar() or 0
    
    # Worlds count
    worlds_result = await db.execute(
        select(func.count(World.id)).filter(World.user_id == user_id)
    )
    worlds_count = worlds_result.scalar() or 0
    
    # Characters count
    characters_result = await db.execute(
        select(func.count(Character.id)).filter(
            and_(Character.world.has(World.user_id == user_id))
        )
    )
    characters_count = characters_result.scalar() or 0
    
    # Locations count
    locations_result = await db.execute(
        select(func.count(Location.id)).filter(
            and_(Location.world.has(World.user_id == user_id))
        )
    )
    locations_count = locations_result.scalar() or 0
    
    # Lore items count
    lore_items_result = await db.execute(
        select(func.count(LoreItem.id)).filter(
            and_(LoreItem.world.has(World.user_id == user_id))
        )
    )
    lore_items_count = lore_items_result.scalar() or 0
    
    # Acts count
    acts_result = await db.execute(
        select(func.count(Act.id)).filter(
            and_(Act.story.has(Story.user_id == user_id))
        )
    )
    acts_count = acts_result.scalar() or 0
    
    # Scenes count
    scenes_result = await db.execute(
        select(func.count(Scene.id)).filter(
            and_(Scene.act.has(Act.story.has(Story.user_id == user_id)))
        )
    )
    scenes_count = scenes_result.scalar() or 0
    
    # AI usage statistics
    ai_calls_result = await db.execute(
        select(func.count(AICallLog.id)).filter(AICallLog.user_id == user_id)
    )
    ai_calls_count = ai_calls_result.scalar() or 0
    
    total_cost_result = await db.execute(
        select(func.sum(AICallLog.calculated_cost_usd)).filter(AICallLog.user_id == user_id)
    )
    total_ai_cost = total_cost_result.scalar() or 0.0
    
    return {
        "stories_count": stories_count,
        "worlds_count": worlds_count,
        "characters_count": characters_count,
        "locations_count": locations_count,
        "lore_items_count": lore_items_count,
        "acts_count": acts_count,
        "scenes_count": scenes_count,
        "ai_calls_count": ai_calls_count,
        "total_ai_cost": float(total_ai_cost)
    }

# Create CRUD class for consistency with other modules
class UserCRUD:
    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[model_user.User]:
        return await get_user(db, user_id)
    
    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[model_user.User]:
        return await get_user_by_username(db, username)
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[model_user.User]:
        return await get_user_by_email(db, email)
    
    async def get_user_by_reset_token(self, db: AsyncSession, reset_token: str) -> Optional[model_user.User]:
        return await get_user_by_reset_token(db, reset_token)
    
    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[model_user.User]:
        return await get_users(db, skip, limit)
    
    async def create_user(self, db: AsyncSession, user: schema_user.UserCreate) -> model_user.User:
        return await create_user(db, user)
    
    async def update_user(self, db: AsyncSession, db_user: model_user.User, user_in: schema_user.UserUpdate) -> model_user.User:
        return await update_user(db, db_user, user_in)
    
    async def delete_user(self, db: AsyncSession, user_id: int) -> Optional[model_user.User]:
        return await delete_user(db, user_id)

user_crud = UserCRUD()