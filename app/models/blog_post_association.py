"""Blog post association model for linking posts to stories, worlds, etc."""
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.blog_post import BlogPost


class AssociationType(str, Enum):
    """Enum for association types."""
    STORY = "story"
    WORLD = "world"
    CHARACTER = "character"
    LOCATION = "location"
    LORE_ITEM = "lore_item"


class BlogPostAssociation(Base):
    """Blog post association model for linking posts to storytelling elements."""
    __tablename__ = "blog_post_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Post relationship
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("blog_posts.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Association details
    association_type: Mapped[AssociationType] = mapped_column(
        SQLAlchemyEnum(AssociationType), 
        nullable=False, 
        index=True
    )
    association_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    association_title: Mapped[str] = mapped_column(String(255), nullable=True)  # Cached title for performance
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="associations")
    
    def __repr__(self):
        return f"<BlogPostAssociation(id={self.id}, post_id={self.post_id}, type='{self.association_type}', association_id={self.association_id})>"