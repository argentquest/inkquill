"""SQLAlchemy models for story rating."""

# /story_app/app/models/story_rating.py

import sqlalchemy
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User
    from .published_story import PublishedStory

class StoryRating(Base):
    """
    SQLAlchemy ORM Model representing ratings/likes for published stories.
    Each user can rate a story once with a value between 1-5.
    """
    __tablename__ = "story_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    published_story_id: Mapped[int] = mapped_column(Integer, ForeignKey("published_stories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Rating value (1-5 stars)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    published_story: Mapped["PublishedStory"] = relationship("PublishedStory", back_populates="ratings")
    rater: Mapped["User"] = relationship("User", back_populates="story_ratings")

    # Constraints
    __table_args__ = (
        UniqueConstraint('published_story_id', 'user_id', name='unique_user_story_rating'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating_range'),
    )

    def __repr__(self):
        return f"<StoryRating(id={self.id}, story_id={self.published_story_id}, user_id={self.user_id}, rating={self.rating})>"
