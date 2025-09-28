"""Blog author profile model for extended author information."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class BlogAuthorProfile(Base):
    """Blog author profile model for extended author information."""
    __tablename__ = "blog_author_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Profile information
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    profile_image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Social links
    website_url: Mapped[str] = mapped_column(String(255), nullable=True)
    twitter_handle: Mapped[str] = mapped_column(String(50), nullable=True)
    instagram_handle: Mapped[str] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Blog settings
    allow_comments_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_publish: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Statistics (cached for performance)
    total_posts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    follower_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="blog_author_profile")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', name='unique_user_profile'),
    )
    
    def __repr__(self):
        return f"<BlogAuthorProfile(id={self.id}, user_id={self.user_id}, total_posts={self.total_posts})>"