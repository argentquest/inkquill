"""SQLAlchemy models for story chat session."""

# /story_app/app/models/story_chat_session.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING, List

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .user import User
    from .story import Story
    from .story_chat_message import StoryChatMessage

class StoryChatSession(Base):
    """
    SQLAlchemy ORM Model representing a chat session with a story.
    
    This allows users to have conversations about their story with AI,
    discussing plot, characters, themes, development ideas, etc.
    """
    __tablename__ = "story_chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Links to story and user
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Optional session description
    
    # Session context - what aspect of the story to focus on
    focus_area: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 'plot', 'characters', 'world', 'general', etc.
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    messages: Mapped[List["StoryChatMessage"]] = relationship(
        "StoryChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<StoryChatSession(id={self.id}, title='{self.title}', story_id={self.story_id}, user_id={self.user_id})>"
