"""Forum models for discussion functionality."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, Boolean, 
    UniqueConstraint, Index, Enum as SQLAlchemyEnum, Table
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.world import World
    from app.models.story import Story
    from app.models.character import Character
    from app.models.location import Location


class ForumCategory(Base):
    """Categories for organizing forum discussions."""
    __tablename__ = "forum_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # For UI icons
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    threads: Mapped[List["ForumThread"]] = relationship("ForumThread", back_populates="category", lazy="selectin")
    
    def __repr__(self):
        return f"<ForumCategory(id={self.id}, name='{self.name}')>"


class ThreadStatus(str, Enum):
    """Enum for thread status."""
    OPEN = "open"
    CLOSED = "closed"
    LOCKED = "locked"
    PINNED = "pinned"


class ForumThread(Base):
    """Forum discussion threads."""
    __tablename__ = "forum_threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[ThreadStatus] = mapped_column(
        SQLAlchemyEnum(ThreadStatus, create_type=True, name="thread_status_enum"), 
        default=ThreadStatus.OPEN
    )
    
    # Foreign keys
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("forum_categories.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Optional associations with world elements
    world_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("worlds.id", ondelete="SET NULL"), nullable=True)
    story_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("stories.id", ondelete="SET NULL"), nullable=True)
    
    # Metadata
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    post_count: Mapped[int] = mapped_column(Integer, default=0)
    last_post_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_post_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Moderation
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category: Mapped["ForumCategory"] = relationship("ForumCategory", back_populates="threads")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="forum_threads")
    last_post_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[last_post_by_id])
    deleted_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[deleted_by_id])
    
    world: Mapped[Optional["World"]] = relationship("World", back_populates="forum_threads")
    story: Mapped[Optional["Story"]] = relationship("Story", back_populates="forum_threads")
    
    posts: Mapped[List["ForumPost"]] = relationship(
        "ForumPost", 
        back_populates="thread", 
        cascade="all, delete-orphan",
        primaryjoin="and_(ForumThread.id==ForumPost.thread_id, ForumPost.is_deleted==False)"
    )
    
    subscriptions: Mapped[List["ForumSubscription"]] = relationship(
        "ForumSubscription", 
        back_populates="thread", 
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_thread_category_status", "category_id", "status"),
        Index("idx_thread_world", "world_id"),
        Index("idx_thread_story", "story_id"),
        UniqueConstraint("category_id", "slug", name="uq_thread_category_slug"),
    )
    
    def __repr__(self):
        return f"<ForumThread(id={self.id}, title='{self.title}')>"


class ForumPost(Base):
    """Individual posts/replies in forum threads."""
    __tablename__ = "forum_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Rendered HTML cache
    
    # Foreign keys
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_post_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=True)
    
    # Optional references to world elements
    character_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("characters.id", ondelete="SET NULL"), nullable=True)
    location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    
    # Voting
    upvote_count: Mapped[int] = mapped_column(Integer, default=0)
    downvote_count: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)  # upvotes - downvotes
    
    # Edit tracking
    edit_count: Mapped[int] = mapped_column(Integer, default=0)
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    edited_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Moderation
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deletion_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    thread: Mapped["ForumThread"] = relationship("ForumThread", back_populates="posts")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="forum_posts")
    edited_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[edited_by_id])
    deleted_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[deleted_by_id])
    
    parent_post: Mapped[Optional["ForumPost"]] = relationship("ForumPost", remote_side=[id], backref="replies")
    
    character: Mapped[Optional["Character"]] = relationship("Character", back_populates="forum_posts")
    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="forum_posts")
    
    votes: Mapped[List["ForumVote"]] = relationship("ForumVote", back_populates="post", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_post_thread_created", "thread_id", "created_at"),
        Index("idx_post_user", "user_id"),
        Index("idx_post_parent", "parent_post_id"),
    )
    
    def __repr__(self):
        return f"<ForumPost(id={self.id}, thread_id={self.thread_id})>"


class VoteType(str, Enum):
    """Enum for vote types."""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"


class ForumVote(Base):
    """Track user votes on forum posts."""
    __tablename__ = "forum_votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    vote_type: Mapped[VoteType] = mapped_column(
        SQLAlchemyEnum(VoteType, create_type=True, name="vote_type_enum"), 
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    post: Mapped["ForumPost"] = relationship("ForumPost", back_populates="votes")
    user: Mapped["User"] = relationship("User", back_populates="forum_votes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_vote_post_user"),
        Index("idx_vote_user", "user_id"),
    )
    
    def __repr__(self):
        return f"<ForumVote(id={self.id}, post_id={self.post_id}, user_id={self.user_id}, type={self.vote_type.value})>"


class ForumSubscription(Base):
    """Track user subscriptions to forum threads for notifications."""
    __tablename__ = "forum_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("forum_threads.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Notification preferences
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_in_app: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    thread: Mapped["ForumThread"] = relationship("ForumThread", back_populates="subscriptions")
    user: Mapped["User"] = relationship("User", back_populates="forum_subscriptions")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("thread_id", "user_id", name="uq_subscription_thread_user"),
        Index("idx_subscription_user", "user_id"),
    )
    
    def __repr__(self):
        return f"<ForumSubscription(id={self.id}, thread_id={self.thread_id}, user_id={self.user_id})>"