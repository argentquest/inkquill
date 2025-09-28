"""Blog category model for organizing blog posts."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.blog_post import BlogPost


class BlogCategory(Base):
    """Blog category model for organizing posts."""
    __tablename__ = "blog_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color code
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Icon class or emoji
    
    # Statistics
    post_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Display settings
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    posts: Mapped[List["BlogPost"]] = relationship("BlogPost", back_populates="category")
    
    def __repr__(self):
        return f"<BlogCategory(id={self.id}, name='{self.name}', slug='{self.slug}')>"