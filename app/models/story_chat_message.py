"""SQLAlchemy models for story chat message."""

# /story_app/app/models/story_chat_message.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING, Dict, Any

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .story_chat_session import StoryChatSession
    from .ai_cost_log import AICallLog

class StoryChatMessage(Base):
    """
    SQLAlchemy ORM Model representing a message in a story chat session.
    
    These messages are conversations about story development, plot discussion,
    character analysis, and other story-related topics.
    """
    __tablename__ = "story_chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Session reference
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("story_chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message details
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # AI context and metadata
    full_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Complete context sent to AI
    story_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Story-specific context used
    
    # Optional targeting for specific story elements
    target_element: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'act', 'scene', 'character', etc.
    target_element_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ID of the target element
    
    # Cost tracking
    cost_log_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_call_logs.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamp
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    session: Mapped["StoryChatSession"] = relationship("StoryChatSession", back_populates="messages")
    cost_log: Mapped[Optional["AICallLog"]] = relationship("AICallLog")

    def __repr__(self):
        return f"<StoryChatMessage(id={self.id}, session_id={self.session_id}, role='{self.role}', target_element='{self.target_element}')>"
