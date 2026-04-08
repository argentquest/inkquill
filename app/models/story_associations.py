"""SQLAlchemy models for story associations."""

# /story_app/app/models/story_associations.py

from sqlalchemy import Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from typing import List, Dict, Any, TYPE_CHECKING

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .story import Story
    from .character import Character
    from .location import Location
    from .lore_item import LoreItem

class StoryCharacterAssociation(Base):
    """SQLAlchemy model for story character association."""
    __tablename__ = "storytelling_story_character_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("storytelling_stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    character_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("storytelling_characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # JSON array of role names
    roles: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Optional notes about this association
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    story: Mapped["Story"] = relationship("Story", back_populates="character_associations")
    character: Mapped["Character"] = relationship("Character", back_populates="story_associations")

    def __repr__(self):
        return f"<StoryCharacterAssociation(story_id={self.story_id}, character_id={self.character_id}, roles={self.roles})>"


class StoryLocationAssociation(Base):
    """SQLAlchemy model for story location association."""
    __tablename__ = "storytelling_story_location_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("storytelling_stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    location_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("storytelling_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # JSON array of role names
    roles: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Optional notes about this association
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    story: Mapped["Story"] = relationship("Story", back_populates="location_associations")
    location: Mapped["Location"] = relationship("Location", back_populates="story_associations")

    def __repr__(self):
        return f"<StoryLocationAssociation(story_id={self.story_id}, location_id={self.location_id}, roles={self.roles})>"


class StoryLoreItemAssociation(Base):
    """SQLAlchemy model for story lore item association."""
    __tablename__ = "storytelling_story_lore_item_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("storytelling_stories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    lore_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("storytelling_lore_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # JSON array of role names
    roles: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Optional notes about this association
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    story: Mapped["Story"] = relationship("Story", back_populates="lore_item_associations")
    lore_item: Mapped["LoreItem"] = relationship("LoreItem", back_populates="story_associations")

    def __repr__(self):
        return f"<StoryLoreItemAssociation(story_id={self.story_id}, lore_item_id={self.lore_item_id}, roles={self.roles})>"
