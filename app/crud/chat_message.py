"""Database CRUD helpers for chat message."""

# /story_app/app/crud/chat_message.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from typing import List, Optional

from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatMessageCreate


async def create_chat_message(
    db: AsyncSession, 
    message_data: ChatMessageCreate, 
    session_id: int,
    cost_log_id: Optional[int] = None
) -> ChatMessage:
    """Create a new chat message"""
    db_message = ChatMessage(
        session_id=session_id,
        role=message_data.role,
        content=message_data.content,
        full_context=message_data.full_context,
        element_type=message_data.element_type,
        element_id=message_data.element_id,
        cost_log_id=cost_log_id
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message


async def get_chat_messages_by_session(
    db: AsyncSession, 
    session_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ChatMessage]:
    """Get all messages for a session, ordered chronologically"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_chat_message(
    db: AsyncSession, 
    message_id: int
) -> Optional[ChatMessage]:
    """Get a specific chat message by ID"""
    result = await db.execute(
        select(ChatMessage)
        .options(selectinload(ChatMessage.cost_log))
        .where(ChatMessage.id == message_id)
    )
    return result.scalar_one_or_none()


async def get_conversation_context(
    db: AsyncSession, 
    session_id: int,
    limit: int = 20
) -> List[ChatMessage]:
    """Get recent conversation context for AI processing"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    # Return in chronological order (oldest first)
    return list(reversed(messages))


async def delete_chat_message(
    db: AsyncSession, 
    message_id: int
) -> bool:
    """Delete a chat message"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.id == message_id)
    )
    db_message = result.scalar_one_or_none()
    
    if not db_message:
        return False
    
    await db.delete(db_message)
    await db.commit()
    return True


async def get_messages_count_by_session(
    db: AsyncSession, 
    session_id: int
) -> int:
    """Get total count of messages in a session"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
    )
    return len(result.scalars().all())


async def get_element_specific_messages(
    db: AsyncSession,
    session_id: int,
    element_type: str,
    element_id: int,
    limit: int = 10
) -> List[ChatMessage]:
    """Get messages related to a specific element"""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .where(ChatMessage.element_type == element_type)
        .where(ChatMessage.element_id == element_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    return list(reversed(messages))  # Return chronologically

# Create CRUD class for consistency
class ChatMessageCRUD:
    """Class for chat message c r u d."""
    async def create_chat_message(self, db: AsyncSession, message_data: ChatMessageCreate, 
                                 session_id: int = None, cost_log_id: Optional[int] = None) -> ChatMessage:
        if session_id is None:
            session_id = message_data.chat_session_id
        return await create_chat_message(db, message_data, session_id, cost_log_id)
    
    async def get_messages_by_session(self, db: AsyncSession, session_id: int, 
                                     limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        return await get_chat_messages_by_session(db, session_id, offset, limit)
    
    async def get_chat_message(self, db: AsyncSession, message_id: int) -> Optional[ChatMessage]:
        return await get_chat_message(db, message_id)
    
    async def get_conversation_context(self, db: AsyncSession, session_id: int, 
                                     limit: int = 10) -> List[ChatMessage]:
        return await get_conversation_context(db, session_id, limit)
    
    async def delete_chat_message(self, db: AsyncSession, message_id: int) -> bool:
        return await delete_chat_message(db, message_id)
    
    async def get_messages_count_by_session(self, db: AsyncSession, session_id: int) -> int:
        return await get_messages_count_by_session(db, session_id)
    
    async def get_element_specific_messages(self, db: AsyncSession, session_id: int, 
                                          element_type: str, element_id: int, limit: int = 10) -> List[ChatMessage]:
        return await get_element_specific_messages(db, session_id, element_type, element_id, limit)

chat_message_crud = ChatMessageCRUD()
