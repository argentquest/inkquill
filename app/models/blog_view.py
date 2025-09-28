"""Blog view model for tracking post views and analytics."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INET

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.blog_post import BlogPost


class BlogView(Base):
    """Blog view model for tracking post views and analytics."""
    __tablename__ = "blog_views"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Post relationship
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("blog_posts.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # User relationship (optional for anonymous views)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    
    # Analytics data
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True, index=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referrer_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Engagement metrics
    view_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # seconds spent reading
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="views")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="blog_views")
    
    def __repr__(self):
        try:
            return f"<BlogView(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"
        except Exception:
            # Handle detached instance case
            return f"<BlogView(detached instance at {hex(id(self))})>"