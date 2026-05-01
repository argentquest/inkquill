"""CRUD operations for standalone chatbot sessions and messages."""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc

from app.models.chatbot_session import ChatbotSession
from app.models.chatbot_message import ChatbotMessage

logger = logging.getLogger(__name__)


async def create_session(db: AsyncSession, user_id: int, title: str) -> ChatbotSession:
    session = ChatbotSession(user_id=user_id, title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_sessions(db: AsyncSession, user_id: int, limit: int = 50) -> List[ChatbotSession]:
    result = await db.execute(
        select(ChatbotSession)
        .where(ChatbotSession.user_id == user_id)
        .order_by(desc(ChatbotSession.updated_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_session(db: AsyncSession, session_id: int, user_id: int) -> Optional[ChatbotSession]:
    result = await db.execute(
        select(ChatbotSession)
        .where(ChatbotSession.id == session_id)
        .where(ChatbotSession.user_id == user_id)
        .options(selectinload(ChatbotSession.messages))
    )
    return result.scalar_one_or_none()


async def update_session_title(db: AsyncSession, session: ChatbotSession, title: str) -> ChatbotSession:
    session.title = title
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def delete_session(db: AsyncSession, session: ChatbotSession) -> None:
    await db.delete(session)
    await db.commit()


async def create_message(
    db: AsyncSession,
    session_id: int,
    role: str,
    content: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    cost_usd: Optional[float] = None,
    model_name: Optional[str] = None,
) -> ChatbotMessage:
    msg = ChatbotMessage(
        session_id=session_id,
        role=role,
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
        model_name=model_name,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
