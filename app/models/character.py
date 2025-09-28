# /ai_rag_story_app/app/models/character.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .world import World
    from .story import Story
    from .generated_image import GeneratedImage
    from .location import Location
    from .forum import ForumPost
    from .story_associations import StoryCharacterAssociation
    from .act_associations import ActCharacterAssociation
    from .scene_associations import SceneCharacterAssociation

# --- Association Table for Story-Character Many-to-Many Relationship ---
story_character_association_table = sqlalchemy.Table(
    "story_character_association",
    Base.metadata,
    Column("story_id", Integer, ForeignKey("stories.id", ondelete="CASCADE"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
    Column("role_in_story", String(255), nullable=True)
)

class Character(Base):
    """
    SQLAlchemy ORM Model representing a Character within a World.
    """
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    species: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personality_traits: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    backstory: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # This field is now legacy, but we keep it for now. The canonical path is in GeneratedImage.
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    world_id: Mapped[int] = mapped_column(Integer, ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    
    current_location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    placement_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    current_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True)
    
    # AI import fields
    importance_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    relationships: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Character generator fields
    core_motivation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Legacy field
    core_motivations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # New multiple motivations field
    physical_attributes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    key_relationships: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    genre_specific_answers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    generated_narrative: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_ai_generated: Mapped[Optional[bool]] = mapped_column(nullable=True, default=False)
    
    # New character generator fields
    next_quest_scenario: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_meeting_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    age_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    profession: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    short_backstory: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    visual_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    narrative_filter_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---

    world: Mapped["World"] = relationship("World", back_populates="characters")

    stories: Mapped[List["Story"]] = relationship(
        "Story",
        secondary=story_character_association_table,
        back_populates="characters"
    )
    
    current_location: Mapped[Optional["Location"]] = relationship("Location", foreign_keys=[current_location_id])

    # --- Relationships to generated images ---
    images: Mapped[List["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="and_(GeneratedImage.element_type=='character', foreign(GeneratedImage.associated_element_id)==Character.id)",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    current_image: Mapped[Optional["GeneratedImage"]] = relationship(
        "GeneratedImage",
        # Use the string class name 'Character' in the join condition
        primaryjoin="foreign(Character.current_image_id)==GeneratedImage.id",
        lazy="selectin"
    )

    # Forum relationships
    forum_posts: Mapped[List["ForumPost"]] = relationship(
        "ForumPost",
        back_populates="character"
    )
    
    # New role-based associations
    story_associations: Mapped[List["StoryCharacterAssociation"]] = relationship("StoryCharacterAssociation", back_populates="character", cascade="all, delete-orphan")
    act_associations: Mapped[List["ActCharacterAssociation"]] = relationship("ActCharacterAssociation", back_populates="character", cascade="all, delete-orphan")
    scene_associations: Mapped[List["SceneCharacterAssociation"]] = relationship("SceneCharacterAssociation", back_populates="character", cascade="all, delete-orphan")

    @property
    def image_url(self) -> Optional[str]:
        """Return the image URL for this character if it has a current image."""
        if self.current_image and self.current_image.blob_path:
            from app.core.config import settings
            if settings.AZURE_STORAGE_ACCOUNT_NAME:
                container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
                return f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{self.current_image.blob_path}"
            else:
                # Fallback: assume blob_path is already a full URL
                return self.current_image.blob_path
        return None

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', world_id={self.world_id})>"