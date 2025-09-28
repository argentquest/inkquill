"""Blog tag models for tagging blog posts."""
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.blog_post import BlogPost


# Association table for many-to-many relationship between posts and tags
blog_post_tags = Table(
    'blog_post_tags',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('post_id', Integer, ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False),
    Column('tag_id', Integer, ForeignKey('blog_tags.id', ondelete='CASCADE'), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    # Unique constraint to prevent duplicate associations
    # UniqueConstraint would be imported from sqlalchemy if needed
)


class BlogTag(Base):
    """Blog tag model for categorizing posts with flexible tags."""
    __tablename__ = "blog_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    posts: Mapped[List["BlogPost"]] = relationship("BlogPost", secondary=blog_post_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<BlogTag(id={self.id}, name='{self.name}', usage_count={self.usage_count})>"