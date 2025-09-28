# /ai_rag_story_app/app/models/chat_message.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING, Dict, Any

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .chat_session import ChatSession
    from .ai_cost_log import AICallLog

class ChatMessage(Base):
    """
    SQLAlchemy ORM Model representing a message in a chat session.
    """
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    full_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Complete context sent to AI
    
    # Optional fields for element-specific chats
    element_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'character', 'location', etc.
    element_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Cost tracking
    cost_log_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_call_logs.id", ondelete="SET NULL"), nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    cost_log: Mapped[Optional["AICallLog"]] = relationship("AICallLog")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role='{self.role}', element_type='{self.element_type}')>"