"""SQLAlchemy models for story."""

# /story_app/app/models/story.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .user import User
    from .act import Act
    from .world import World 
    from .character import Character
    from .location import Location
    from .lore_item import LoreItem
    from .generated_image import GeneratedImage # Import GeneratedImage
    from .forum import ForumThread
    from .story_associations import StoryCharacterAssociation, StoryLocationAssociation, StoryLoreItemAssociation
    from .published_story import PublishedStory
    from .story_chat_session import StoryChatSession

from .character import story_character_association_table
from .location import story_location_association_table
from .lore_item import story_lore_item_association_table

class Story(Base):
    """SQLAlchemy model for story."""
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    short_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Writer's intent/summary
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # AI-generated summary
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    world_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("worlds.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Story type for Basic/Advanced story system
    story_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='advanced',
        server_default='advanced',
        index=True
    )  # Values: 'basic', 'advanced'
    
    # --- FIX: Add fields for image support ---
    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    current_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True)
    # --- END FIX ---
    
    # Story generation metadata fields
    story_genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    story_tone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    primary_conflict_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    OwnerUser: Mapped["User"] = relationship("User", back_populates="created_stories")
    acts: Mapped[List["Act"]] = relationship("Act", back_populates="story", cascade="all, delete-orphan", order_by="Act.act_number")
    world: Mapped["World"] = relationship("World", back_populates="stories")

    # Legacy simple associations (keeping for backward compatibility)
    characters: Mapped[List["Character"]] = relationship("Character", secondary=story_character_association_table, back_populates="stories")
    locations: Mapped[List["Location"]] = relationship("Location", secondary=story_location_association_table, back_populates="stories")
    lore_items: Mapped[List["LoreItem"]] = relationship("LoreItem", secondary=story_lore_item_association_table, back_populates="stories")
    
    # New role-based associations
    character_associations: Mapped[List["StoryCharacterAssociation"]] = relationship("StoryCharacterAssociation", back_populates="story", cascade="all, delete-orphan")
    location_associations: Mapped[List["StoryLocationAssociation"]] = relationship("StoryLocationAssociation", back_populates="story", cascade="all, delete-orphan")
    lore_item_associations: Mapped[List["StoryLoreItemAssociation"]] = relationship("StoryLoreItemAssociation", back_populates="story", cascade="all, delete-orphan")
    
    # --- FIX: Add relationships for images ---
    images: Mapped[List["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="and_(GeneratedImage.element_type=='story', foreign(GeneratedImage.associated_element_id)==Story.id)",
        cascade="all, delete-orphan",
        lazy="selectin",
        overlaps="images" 
    )
    
    current_image: Mapped[Optional["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="foreign(Story.current_image_id)==GeneratedImage.id",
        lazy="selectin"
    )
    # --- END FIX ---

    # Forum relationships
    forum_threads: Mapped[List["ForumThread"]] = relationship(
        "ForumThread",
        back_populates="story"
    )
    
    # Publishing relationship
    published_version: Mapped[Optional["PublishedStory"]] = relationship(
        "PublishedStory",
        back_populates="story",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # Story chat sessions relationship - temporarily disabled until tables exist
    # chat_sessions: Mapped[List["StoryChatSession"]] = relationship(
    #     "StoryChatSession",
    #     back_populates="story",
    #     cascade="all, delete-orphan",
    #     order_by="StoryChatSession.updated_at.desc()"
    # )

    @property
    def image_url(self) -> Optional[str]:
        """
        Return the image URL for this story.
        This property is mainly for template compatibility.
        For actual URL generation, use _check_and_get_image_url in views.
        """
        # This is a simplified version for templates
        # The actual URL should be generated by _check_and_get_image_url
        # which checks if the blob actually exists
        if self.current_image:
            return self.current_image.blob_url
        elif self.image_blob_path:
            # For legacy image_blob_path, assume it's already a full URL
            return self.image_blob_path
        return None

    def __repr__(self):
        return f"<Story(id={self.id}, title='{self.title}', user_id={self.user_id}, world_id={self.world_id})>"
