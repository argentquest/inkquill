"""SQLAlchemy models for act."""

# /story_app/app/models/act.py

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING # Added List

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .story import Story  # For relationship type hinting
    from .prompt import Prompt # For relationship to a system prompt
    from .scene import Scene # <<< NEW: Import Scene model for relationship
    from .story_class import StoryClass
    from .generated_image import GeneratedImage
    from .act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation

# --- Background: SQLAlchemy ORM Model ---
# This file defines the `Act` model using SQLAlchemy's ORM.
# This Python class maps to the `acts` table in the PostgreSQL database.
# Each Act belongs to a specific Story and represents a distinct part of that story,
# ordered by its `act_number`. It now includes fields for a summary, writer's notes,
# a link to a system prompt, and a relationship to its Scenes.

class Act(Base):
    """
    SQLAlchemy ORM Model representing an Act within a Story.
    """
    __tablename__ = "storytelling_acts"

    # --- Table Columns ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Main content (HTML from Quill)
    act_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- New Fields (from previous update) ---
    act_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Writer's intent/summary
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated summary
    writer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Custom image generation prompt
    system_prompt_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("prompts.id", ondelete="SET NULL"), 
        nullable=True,
        index=True 
    )
    # --- End New Fields ---

    # --- Story Class Assignment ---
    story_class_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("storytelling_story_classes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    # --- End Story Class Assignment ---

    story_id: Mapped[int] = mapped_column(Integer, ForeignKey("storytelling_stories.id", ondelete="CASCADE"), nullable=False)
    
    current_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    story: Mapped["Story"] = relationship("Story", back_populates="acts")
    system_prompt: Mapped[Optional["Prompt"]] = relationship("Prompt", foreign_keys=[system_prompt_id])
    story_class: Mapped[Optional["StoryClass"]] = relationship("StoryClass", back_populates="acts")

    # --- NEW: Relationship to Scenes ---
    # An Act can have multiple Scenes.
    # If an Act is deleted, all its associated Scenes will also be deleted due to cascade.
    scenes: Mapped[List["Scene"]] = relationship(
        "Scene",
        back_populates="act", # Must match the relationship name in the Scene model pointing back to Act
        cascade="all, delete-orphan", # Ensures scenes are deleted when their parent act is deleted
        order_by="Scene.scene_number", # Default order for accessing act.scenes
        lazy="selectin" # Or "joined" - Eager load scenes when an Act is fetched
    )
    # --- End NEW Relationship ---
    
    # --- Relationships to generated images ---
    images: Mapped[List["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="and_(GeneratedImage.element_type=='act', foreign(GeneratedImage.associated_element_id)==Act.id)",
        cascade="all, delete-orphan",
        lazy="selectin",
        overlaps="images"
    )
    
    current_image: Mapped[Optional["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="foreign(Act.current_image_id)==GeneratedImage.id",
        lazy="selectin"
    )
    # --- End image relationships ---
    
    # --- NEW: Act Element Associations with Roles ---
    character_associations: Mapped[List["ActCharacterAssociation"]] = relationship("ActCharacterAssociation", back_populates="act", cascade="all, delete-orphan")
    location_associations: Mapped[List["ActLocationAssociation"]] = relationship("ActLocationAssociation", back_populates="act", cascade="all, delete-orphan")
    lore_item_associations: Mapped[List["ActLoreItemAssociation"]] = relationship("ActLoreItemAssociation", back_populates="act", cascade="all, delete-orphan")
    # --- End NEW Associations ---


    # --- Table Constraints ---
    __table_args__ = (
        UniqueConstraint('story_id', 'act_number', name='_story_act_number_uc'),
    )

    @property
    def image_url(self) -> Optional[str]:
        """Return the image URL for this act if it has a current image."""
        if self.current_image and self.current_image.blob_path:
            from app.core.storage_deps import build_storage_url
            return build_storage_url("generated-images", self.current_image.blob_path)
        return None

    def __repr__(self):
        return f"<Act(id={self.id}, title='{self.title}', story_id={self.story_id}, act_number={self.act_number})>"


