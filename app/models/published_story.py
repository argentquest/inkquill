"""SQLAlchemy models for published story."""

# /story_app/app/models/published_story.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User
    from .story import Story
    from .story_comment import StoryComment
    from .story_rating import StoryRating

class PublishedStory(Base):
    """
    SQLAlchemy ORM Model representing a published story.
    Tracks published stories with their metadata, URL, and stats.
    """
    __tablename__ = "published_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Publishing details
    published_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Visibility and status
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    
    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    published_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Search optimization
    search_vector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # For full-text search
    
    # Relationships
    story: Mapped["Story"] = relationship("Story", back_populates="published_version")
    publisher: Mapped["User"] = relationship("User", back_populates="published_stories")
    comments: Mapped[List["StoryComment"]] = relationship("StoryComment", back_populates="published_story", cascade="all, delete-orphan")
    ratings: Mapped[List["StoryRating"]] = relationship("StoryRating", back_populates="published_story", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PublishedStory(id={self.id}, title='{self.title}', story_id={self.story_id})>"
