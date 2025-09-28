"""Blog comment model for threaded discussions."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, Boolean, 
    Enum as SQLAlchemyEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.blog_post import BlogPost


class CommentStatus(str, Enum):
    """Enum for comment status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELETED = "deleted"


class BlogComment(Base):
    """Blog comment model with threading support."""
    __tablename__ = "blog_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Post relationship
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("blog_posts.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Author relationship
    author_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Threading support
    parent_comment_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("blog_comments.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status and moderation
    status: Mapped[CommentStatus] = mapped_column(
        SQLAlchemyEnum(CommentStatus), 
        nullable=False, 
        default=CommentStatus.APPROVED,
        index=True
    )
    
    # Engagement metrics
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reply_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Special flags
    is_author_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # True if post author replied
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="blog_comments", lazy="selectin")
    parent_comment: Mapped[Optional["BlogComment"]] = relationship("BlogComment", remote_side=[id], back_populates="replies")
    replies: Mapped[List["BlogComment"]] = relationship("BlogComment", back_populates="parent_comment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_blog_comments_post_status', 'post_id', 'status'),
        Index('idx_blog_comments_author_created', 'author_id', 'created_at'),
        Index('idx_blog_comments_parent_created', 'parent_comment_id', 'created_at'),
    )
    
    def __repr__(self):
        try:
            return f"<BlogComment(id={self.id}, post_id={self.post_id}, author_id={self.author_id}, status='{self.status}')>"
        except Exception:
            # Handle detached instance case
            return f"<BlogComment(detached instance at {hex(id(self))})>"
    
    @property
    def is_top_level(self) -> bool:
        """Check if this is a top-level comment (not a reply)."""
        return self.parent_comment_id is None
    
    @property
    def depth_level(self) -> int:
        """Calculate the depth level of this comment in the thread."""
        if self.is_top_level:
            return 0
        
        # Calculate depth recursively
        depth = 0
        current = self
        while current.parent_comment_id is not None:
            depth += 1
            if hasattr(current, 'parent_comment') and current.parent_comment:
                current = current.parent_comment
            else:
                # If parent not loaded, we can't calculate further
                # In practice, you'd want to ensure parents are loaded
                break
        return depth