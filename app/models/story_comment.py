# /ai_rag_story_app/app/models/story_comment.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User
    from .published_story import PublishedStory

class StoryComment(Base):
    """
    SQLAlchemy ORM Model representing comments on published stories.
    """
    __tablename__ = "story_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    published_story_id: Mapped[int] = mapped_column(Integer, ForeignKey("published_stories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_comment_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("story_comments.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Comment content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Moderation
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    published_story: Mapped["PublishedStory"] = relationship("PublishedStory", back_populates="comments")
    commenter: Mapped["User"] = relationship("User", back_populates="story_comments")
    parent_comment: Mapped[Optional["StoryComment"]] = relationship("StoryComment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<StoryComment(id={self.id}, story_id={self.published_story_id}, user_id={self.user_id})>"