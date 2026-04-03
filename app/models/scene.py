"""SQLAlchemy models for scene."""

# /story_app/app/models/scene.py

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING, List

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .act import Act
    from .story_class import StoryClass
    from .generated_image import GeneratedImage
    from .scene_associations import SceneCharacterAssociation, SceneLocationAssociation, SceneLoreItemAssociation

class Scene(Base):
    """
    SQLAlchemy ORM Model representing a Scene within an Act.
    """
    __tablename__ = "scenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    scene_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Writer's intent/summary
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated summary
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    characters_present: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plot_points: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mood: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Custom image generation prompt

    act_id: Mapped[int] = mapped_column(Integer, ForeignKey("acts.id", ondelete="CASCADE"), nullable=False)

    story_class_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("story_classes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    current_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    act: Mapped["Act"] = relationship("Act", back_populates="scenes")
    story_class: Mapped[Optional["StoryClass"]] = relationship("StoryClass", back_populates="scenes")
    
    # --- Relationships to generated images ---
    images: Mapped[List["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="and_(GeneratedImage.element_type=='scene', foreign(GeneratedImage.associated_element_id)==Scene.id)",
        cascade="all, delete-orphan",
        lazy="selectin",
        overlaps="images" # <-- FIX: Added overlaps parameter
    )
    
    current_image: Mapped[Optional["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="foreign(Scene.current_image_id)==GeneratedImage.id",
        lazy="selectin"
    )
    
    # --- Association relationships ---
    character_associations: Mapped[List["SceneCharacterAssociation"]] = relationship(
        "SceneCharacterAssociation", 
        back_populates="scene", 
        cascade="all, delete-orphan"
    )
    location_associations: Mapped[List["SceneLocationAssociation"]] = relationship(
        "SceneLocationAssociation", 
        back_populates="scene", 
        cascade="all, delete-orphan"
    )
    lore_item_associations: Mapped[List["SceneLoreItemAssociation"]] = relationship(
        "SceneLoreItemAssociation", 
        back_populates="scene", 
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint('act_id', 'scene_number', name='_act_scene_number_uc'),
    )

    @property
    def image_url(self) -> Optional[str]:
        """Return the image URL for this scene if it has a current image."""
        if self.current_image and self.current_image.blob_path:
            from app.core.storage_deps import build_storage_url
            return build_storage_url("generated-images", self.current_image.blob_path)
        return None

    def __repr__(self):
        return f"<Scene(id={self.id}, title='{self.title}', act_id={self.act_id}, scene_number={self.scene_number})>"

