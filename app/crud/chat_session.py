# /ai_rag_story_app/app/crud/chat_session.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatSessionCreate, ChatSessionUpdate


async def create_chat_session(
    db: AsyncSession, 
    session_data: ChatSessionCreate, 
    user_id: int
) -> ChatSession:
    """Create a new chat session"""
    db_session = ChatSession(
        world_id=session_data.world_id,
        user_id=user_id,
        title=session_data.title
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session


async def get_chat_session(
    db: AsyncSession, 
    session_id: int, 
    user_id: int
) -> Optional[ChatSession]:
    """Get a chat session by ID for a specific user"""
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
        .where(ChatSession.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_chat_sessions_by_world(
    db: AsyncSession, 
    world_id: int, 
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[ChatSession]:
    """Get all chat sessions for a world, ordered by most recent first"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.world_id == world_id)
        .where(ChatSession.user_id == user_id)
        .order_by(desc(ChatSession.updated_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_chat_session(
    db: AsyncSession, 
    session_id: int, 
    user_id: int, 
    session_update: ChatSessionUpdate
) -> Optional[ChatSession]:
    """Update a chat session"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .where(ChatSession.user_id == user_id)
    )
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        return None
    
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    # Update the updated_at timestamp
    db_session.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_session)
    return db_session


async def delete_chat_session(
    db: AsyncSession, 
    session_id: int, 
    user_id: int
) -> bool:
    """Delete a chat session"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .where(ChatSession.user_id == user_id)
    )
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        return False
    
    await db.delete(db_session)
    await db.commit()
    return True


async def get_chat_sessions_count_by_world(
    db: AsyncSession, 
    world_id: int, 
    user_id: int
) -> int:
    """Get total count of chat sessions for a world"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.world_id == world_id)
        .where(ChatSession.user_id == user_id)
    )
    return len(result.scalars().all())


async def touch_session_updated_at(
    db: AsyncSession, 
    session_id: int
) -> None:
    """Update the updated_at timestamp of a session (called when new message is added)"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
    )
    db_session = result.scalar_one_or_none()
    
    if db_session:
        db_session.updated_at = datetime.utcnow()
        await db.commit()

# Create CRUD class for consistency
class ChatSessionCRUD:
    async def create_chat_session(self, db: AsyncSession, session_data: ChatSessionCreate, user_id: int) -> ChatSession:
        return await create_chat_session(db, session_data, user_id)
    
    async def get_chat_session(self, db: AsyncSession, session_id: int, user_id: int) -> Optional[ChatSession]:
        return await get_chat_session(db, session_id, user_id)
    
    async def get_chat_sessions_by_world(self, db: AsyncSession, world_id: int, user_id: int, 
                                        limit: int = 50, offset: int = 0) -> List[ChatSession]:
        return await get_chat_sessions_by_world(db, world_id, user_id, limit, offset)
    
    async def update_chat_session(self, db: AsyncSession, session_id: int, 
                                 session_update: ChatSessionUpdate) -> Optional[ChatSession]:
        return await update_chat_session(db, session_id, session_update)
    
    async def delete_chat_session(self, db: AsyncSession, session_id: int) -> bool:
        return await delete_chat_session(db, session_id)
    
    async def get_chat_sessions_count_by_world(self, db: AsyncSession, world_id: int, user_id: int) -> int:
        return await get_chat_sessions_count_by_world(db, world_id, user_id)
    
    async def touch_session_updated_at(self, db: AsyncSession, session_id: int) -> None:
        return await touch_session_updated_at(db, session_id)

chat_session_crud = ChatSessionCRUD()