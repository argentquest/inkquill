"""Blog content link model for linking to world elements within post content."""
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.blog_post import BlogPost


class LinkType(str, Enum):
    """Enum for content link types."""
    CHARACTER = "character"
    LOCATION = "location"
    LORE_ITEM = "lore_item"


class BlogContentLink(Base):
    """Blog content link model for linking to world elements within post content."""
    __tablename__ = "blog_content_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Post relationship
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("blog_posts.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Link details
    link_type: Mapped[LinkType] = mapped_column(
        SQLAlchemyEnum(LinkType), 
        nullable=False, 
        index=True
    )
    link_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    link_text: Mapped[str] = mapped_column(String(255), nullable=True)  # The text that was linked
    link_context: Mapped[str] = mapped_column(Text, nullable=True)  # Surrounding context
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="content_links")
    
    def __repr__(self):
        return f"<BlogContentLink(id={self.id}, post_id={self.post_id}, type='{self.link_type}', link_id={self.link_id})>"