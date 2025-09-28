"""Blog follow model for following blog authors."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class BlogFollow(Base):
    """Blog follow model for users following blog authors."""
    __tablename__ = "blog_follows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Author being followed
    author_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Follower
    follower_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Notification settings
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id], back_populates="blog_followers")
    follower: Mapped["User"] = relationship("User", foreign_keys=[follower_id], back_populates="blog_following")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('author_id', 'follower_id', name='unique_author_follower'),
    )
    
    def __repr__(self):
        return f"<BlogFollow(id={self.id}, author_id={self.author_id}, follower_id={self.follower_id})>"