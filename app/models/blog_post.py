"""Blog post model for the blogging engine."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, Boolean, 
    Index, Enum as SQLAlchemyEnum, DECIMAL
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.blog_category import BlogCategory
    from app.models.blog_tag import BlogTag
    from app.models.blog_comment import BlogComment
    from app.models.blog_like import BlogLike
    from app.models.blog_view import BlogView
    from app.models.blog_post_association import BlogPostAssociation
    from app.models.blog_content_link import BlogContentLink
    from app.models.blog_analytics_summary import BlogAnalyticsSummary


class BlogPostStatus(str, Enum):
    """Enum for blog post status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BlogPost(Base):
    """Blog post model."""
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    featured_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status and publishing
    status: Mapped[BlogPostStatus] = mapped_column(
        SQLAlchemyEnum(BlogPostStatus), 
        nullable=False, 
        default=BlogPostStatus.DRAFT,
        index=True
    )
    
    # Author relationship
    author_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Category relationship
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("blog_categories.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    
    # Engagement metrics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # SEO fields
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Open Graph fields
    og_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    og_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    og_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Content flags
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_comments: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Full-text search vector (PostgreSQL specific)
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, nullable=True)
    
    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="blog_posts", lazy="selectin")
    category: Mapped[Optional["BlogCategory"]] = relationship("BlogCategory", back_populates="posts", lazy="selectin")
    tags: Mapped[List["BlogTag"]] = relationship("BlogTag", secondary="blog_post_tags", back_populates="posts", lazy="selectin")
    comments: Mapped[List["BlogComment"]] = relationship("BlogComment", back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[List["BlogLike"]] = relationship("BlogLike", back_populates="post", cascade="all, delete-orphan")
    views: Mapped[List["BlogView"]] = relationship("BlogView", back_populates="post", cascade="all, delete-orphan")
    associations: Mapped[List["BlogPostAssociation"]] = relationship("BlogPostAssociation", back_populates="post", cascade="all, delete-orphan")
    content_links: Mapped[List["BlogContentLink"]] = relationship("BlogContentLink", back_populates="post", cascade="all, delete-orphan")
    analytics_summaries: Mapped[List["BlogAnalyticsSummary"]] = relationship("BlogAnalyticsSummary", back_populates="post", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_blog_posts_author_status', 'author_id', 'status'),
        Index('idx_blog_posts_published_featured', 'published_at', 'is_featured'),
        Index('idx_blog_posts_category_status', 'category_id', 'status'),
        Index('idx_blog_posts_search_vector', 'search_vector', postgresql_using='gin'),
    )
    
    def __repr__(self):
        try:
            return f"<BlogPost(id={self.id}, title='{self.title}', status='{self.status}')>"
        except Exception:
            # Handle detached instance case
            return f"<BlogPost(detached instance at {hex(id(self))})>"
    
    @property
    def is_published(self) -> bool:
        """Check if the post is published."""
        return self.status == BlogPostStatus.PUBLISHED and self.published_at is not None
    
    @property
    def reading_time_minutes(self) -> int:
        """Estimate reading time in minutes (assuming 200 words per minute)."""
        if not self.content:
            return 0
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))