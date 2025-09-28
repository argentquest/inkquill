"""Blog like model for tracking post likes."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.blog_post import BlogPost


class BlogLike(Base):
    """Blog like model for tracking user likes on posts."""
    __tablename__ = "blog_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Post relationship
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("blog_posts.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # User relationship
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="likes")
    user: Mapped["User"] = relationship("User", back_populates="blog_likes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='unique_post_like'),
    )
    
    def __repr__(self):
        try:
            return f"<BlogLike(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"
        except Exception:
            # Handle detached instance case
            return f"<BlogLike(detached instance at {hex(id(self))})>"