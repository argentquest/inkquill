"""SQLAlchemy models for world."""

# /story_app/app/models/world.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING, Dict, Any

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .user import User
    from .story import Story
    from .character import Character
    from .location import Location
    from .lore_item import LoreItem
    from .story_class import StoryClass
    from .generated_image import GeneratedImage # Import GeneratedImage
    from .chat_session import ChatSession
    from .forum import ForumThread
    from .world_role import WorldRole
    from .world_collaborator import WorldCollaborator

class World(Base):
    """
    SQLAlchemy ORM Model representing a creative World.
    A World is owned by a User and can contain Characters, Locations, LoreItems,
    and can be associated with multiple Stories.
    """
    __tablename__ = "worlds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False, unique=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    world_builder_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # --- FIX: Add fields for image support ---
    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    current_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True)
    # --- END FIX ---
    
    # Public access control
    is_free_chat_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    
    # Shadow world flag for Basic/Advanced story system
    is_shadow: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False,
        server_default='false',
        index=True
    )  # True for shadow worlds created for Basic Stories

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    owner: Mapped["User"] = relationship("User", back_populates="worlds")
    stories: Mapped[List["Story"]] = relationship("Story", back_populates="world")
    characters: Mapped[List["Character"]] = relationship("Character", back_populates="world", cascade="all, delete-orphan", order_by="Character.name")
    locations: Mapped[List["Location"]] = relationship("Location", back_populates="world", cascade="all, delete-orphan", order_by="Location.name")
    lore_items: Mapped[List["LoreItem"]] = relationship("LoreItem", back_populates="world", cascade="all, delete-orphan", order_by="LoreItem.title")
    story_classes: Mapped[List["StoryClass"]] = relationship("StoryClass", back_populates="world", cascade="all, delete-orphan", order_by="StoryClass.name")

    # --- FIX: Add relationships for images ---
    images: Mapped[List["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="and_(GeneratedImage.element_type=='world', foreign(GeneratedImage.associated_element_id)==World.id)",
        cascade="all, delete-orphan",
        lazy="selectin",
        overlaps="images" # Overlaps with Character.images, etc.
    )
    
    current_image: Mapped[Optional["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="foreign(World.current_image_id)==GeneratedImage.id",
        lazy="selectin"
    )
    # --- END FIX ---

    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="world",
        cascade="all, delete-orphan"
    )
    
    custom_roles: Mapped[List["WorldRole"]] = relationship(
        "WorldRole",
        back_populates="world",
        cascade="all, delete-orphan"
    )

    collaborators: Mapped[List["WorldCollaborator"]] = relationship(
        "WorldCollaborator",
        back_populates="world",
        cascade="all, delete-orphan"
    )

    # Forum relationships
    forum_threads: Mapped[List["ForumThread"]] = relationship(
        "ForumThread",
        back_populates="world"
    )

    @property
    def image_url(self) -> Optional[str]:
        """Return the image URL for this world if it has a current image."""
        if self.current_image and self.current_image.blob_path:
            from app.core.storage_deps import build_storage_url
            return build_storage_url("generated-images", self.current_image.blob_path)
        return None

    def __repr__(self):
        return f"<World(id={self.id}, name='{self.name}', user_id={self.user_id})>"

