"""SQLAlchemy models for scene associations."""

# /story_app/app/models/scene_associations.py

from sqlalchemy import Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from typing import List, Dict, Any, TYPE_CHECKING

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .scene import Scene
    from .character import Character
    from .location import Location
    from .lore_item import LoreItem

class SceneCharacterAssociation(Base):
    """SQLAlchemy model for scene character association."""
    __tablename__ = "storytelling_scene_character_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scene_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("storytelling_scenes.id", ondelete="CASCADE"),
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
    scene: Mapped["Scene"] = relationship("Scene", back_populates="character_associations")
    character: Mapped["Character"] = relationship("Character", back_populates="scene_associations")

    def __repr__(self):
        return f"<SceneCharacterAssociation(scene_id={self.scene_id}, character_id={self.character_id}, roles={self.roles})>"


class SceneLocationAssociation(Base):
    """SQLAlchemy model for scene location association."""
    __tablename__ = "storytelling_scene_location_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scene_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("storytelling_scenes.id", ondelete="CASCADE"),
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
    scene: Mapped["Scene"] = relationship("Scene", back_populates="location_associations")
    location: Mapped["Location"] = relationship("Location", back_populates="scene_associations")

    def __repr__(self):
        return f"<SceneLocationAssociation(scene_id={self.scene_id}, location_id={self.location_id}, roles={self.roles})>"


class SceneLoreItemAssociation(Base):
    """SQLAlchemy model for scene lore item association."""
    __tablename__ = "storytelling_scene_lore_item_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scene_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("storytelling_scenes.id", ondelete="CASCADE"),
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
    scene: Mapped["Scene"] = relationship("Scene", back_populates="lore_item_associations")
    lore_item: Mapped["LoreItem"] = relationship("LoreItem", back_populates="scene_associations")

    def __repr__(self):
        return f"<SceneLoreItemAssociation(scene_id={self.scene_id}, lore_item_id={self.lore_item_id}, roles={self.roles})>"
