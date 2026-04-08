"""SQLAlchemy models for lore item."""

# /story_app/app/models/lore_item.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING
import enum

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .world import World
    from .story import Story
    from .generated_image import GeneratedImage
    from .location import Location # Added for current_location relationship
    from .story_associations import StoryLoreItemAssociation
    from .act_associations import ActLoreItemAssociation
    from .scene_associations import SceneLoreItemAssociation

# --- Enum for LoreItem Category ---
class LoreItemCategoryEnum(str, enum.Enum):
    """SQLAlchemy model for lore item category enum."""
    MAGIC_SYSTEM = "MAGIC_SYSTEM"
    HISTORICAL_EVENT = "HISTORICAL_EVENT"
    ARTIFACT = "ARTIFACT"
    DEITY = "DEITY"
    CREATURE = "CREATURE"
    FACTION_ORGANIZATION = "FACTION_ORGANIZATION"
    CULTURE_CUSTOM = "CULTURE_CUSTOM"
    TECHNOLOGY = "TECHNOLOGY"
    PHILOSOPHY_BELIEF = "PHILOSOPHY_BELIEF"
    OTHER_LORE = "OTHER_LORE"

# --- Association Table for Story-LoreItem Many-to-Many Relationship ---
story_lore_item_association_table = sqlalchemy.Table(
    "story_lore_item_association",
    Base.metadata,
    Column("story_id", Integer, ForeignKey("storytelling_stories.id", ondelete="CASCADE"), primary_key=True),
    Column("lore_item_id", Integer, ForeignKey("storytelling_lore_items.id", ondelete="CASCADE"), primary_key=True),
    Column("relevance_to_story", Text, nullable=True)
)

class LoreItem(Base):
    """
    SQLAlchemy ORM Model representing a Lore Item within a World.
    """
    __tablename__ = "storytelling_lore_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    category: Mapped[LoreItemCategoryEnum] = mapped_column(
        SQLAlchemyEnum(
            LoreItemCategoryEnum,
            name="lore_item_category_enum",
            create_type=True
        ),
        nullable=False,
        index=True
    )

    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    world_id: Mapped[int] = mapped_column(Integer, ForeignKey("storytelling_worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    
    current_location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("storytelling_locations.id", ondelete="SET NULL"), nullable=True)
    placement_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    current_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True)
    
    # AI import fields
    importance_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    related_elements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---

    world: Mapped["World"] = relationship("World", back_populates="lore_items")

    stories: Mapped[List["Story"]] = relationship(
        "Story",
        secondary=story_lore_item_association_table,
        back_populates="lore_items"
    )
    
    current_location: Mapped[Optional["Location"]] = relationship("Location", foreign_keys=[current_location_id])

    # --- Relationships to generated images ---
    images: Mapped[List["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="and_(GeneratedImage.element_type=='lore_item', foreign(GeneratedImage.associated_element_id)==LoreItem.id)",
        cascade="all, delete-orphan",
        lazy="selectin",
        overlaps="images" # <-- FIX: Added overlaps parameter
    )
    
    current_image: Mapped[Optional["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="foreign(LoreItem.current_image_id)==GeneratedImage.id",
        lazy="selectin"
    )
    
    # New role-based associations
    story_associations: Mapped[List["StoryLoreItemAssociation"]] = relationship("StoryLoreItemAssociation", back_populates="lore_item", cascade="all, delete-orphan")
    act_associations: Mapped[List["ActLoreItemAssociation"]] = relationship("ActLoreItemAssociation", back_populates="lore_item", cascade="all, delete-orphan")
    scene_associations: Mapped[List["SceneLoreItemAssociation"]] = relationship("SceneLoreItemAssociation", back_populates="lore_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LoreItem(id={self.id}, title='{self.title}', world_id={self.world_id})>"
