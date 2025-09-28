# /ai_rag_story_app/app/models/location.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Boolean, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING
import enum

# --- Core Application Imports ---
from app.db.database import Base

class LocationScaleEnum(enum.Enum):
    """Enum for different scales of locations"""
    REGION = "REGION"
    CITY = "CITY"  
    BUILDING = "BUILDING"
    ROOM = "ROOM"
    AREA = "AREA"
    OBJECT = "OBJECT"
    POINT = "POINT"
    OTHER = "OTHER"

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .world import World
    from .story import Story
    from .generated_image import GeneratedImage
    from .forum import ForumPost
    from .story_associations import StoryLocationAssociation
    from .act_associations import ActLocationAssociation
    from .scene_associations import SceneLocationAssociation

# --- Association Table for Story-Location Many-to-Many Relationship ---
story_location_association_table = sqlalchemy.Table(
    "story_location_association",
    Base.metadata,
    Column("story_id", Integer, ForeignKey("stories.id", ondelete="CASCADE"), primary_key=True),
    Column("location_id", Integer, ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True),
    Column("significance_to_story", Text, nullable=True)
)

class Location(Base):
    """
    SQLAlchemy ORM Model representing a Location within a World.
    """
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    atmosphere: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    significance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    scale: Mapped[Optional[LocationScaleEnum]] = mapped_column(Enum(LocationScaleEnum, name="location_scale_enum"), nullable=True)
    parent_location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    map_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    map_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True) 
    map_z: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    dimension_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dimension_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dimension_z: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dimension_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    current_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True)
    
    # AI import fields
    geography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cultural_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    importance_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    connected_elements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    world_id: Mapped[int] = mapped_column(Integer, ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---

    world: Mapped["World"] = relationship("World", back_populates="locations")

    stories: Mapped[List["Story"]] = relationship(
        "Story",
        secondary=story_location_association_table,
        back_populates="locations"
    )
    
    parent_location: Mapped[Optional["Location"]] = relationship("Location", remote_side=[id], back_populates="child_locations")
    child_locations: Mapped[List["Location"]] = relationship("Location", back_populates="parent_location")
    
    outgoing_connections: Mapped[List["LocationConnection"]] = relationship(
        "LocationConnection", 
        foreign_keys="LocationConnection.from_location_id",
        back_populates="from_location",
        cascade="all, delete-orphan"
    )
    
    incoming_connections: Mapped[List["LocationConnection"]] = relationship(
        "LocationConnection",
        foreign_keys="LocationConnection.to_location_id", 
        back_populates="to_location",
        cascade="all, delete-orphan"
    )

    # --- Relationships to generated images ---
    images: Mapped[List["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="and_(GeneratedImage.element_type=='location', foreign(GeneratedImage.associated_element_id)==Location.id)",
        cascade="all, delete-orphan",
        lazy="selectin",
        overlaps="images" # <-- FIX: Added overlaps parameter
    )
    
    current_image: Mapped[Optional["GeneratedImage"]] = relationship(
        "GeneratedImage",
        primaryjoin="foreign(Location.current_image_id)==GeneratedImage.id",
        lazy="selectin"
    )

    # Forum relationships
    forum_posts: Mapped[List["ForumPost"]] = relationship(
        "ForumPost",
        back_populates="location"
    )
    
    # New role-based associations
    story_associations: Mapped[List["StoryLocationAssociation"]] = relationship("StoryLocationAssociation", back_populates="location", cascade="all, delete-orphan")
    act_associations: Mapped[List["ActLocationAssociation"]] = relationship("ActLocationAssociation", back_populates="location", cascade="all, delete-orphan")
    scene_associations: Mapped[List["SceneLocationAssociation"]] = relationship("SceneLocationAssociation", back_populates="location", cascade="all, delete-orphan")

    @property
    def image_url(self) -> Optional[str]:
        """Return the image URL for this location if it has a current image."""
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
        return f"<Location(id={self.id}, name='{self.name}', world_id={self.world_id})>"


class LocationConnection(Base):
    """
    SQLAlchemy ORM Model representing connections between locations.
    """
    __tablename__ = "location_connections"

    from_location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True, index=True)
    to_location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True, index=True)
    path_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reverse_path_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    dm_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False) # Made not nullable
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False) # Made not nullable

    from_location: Mapped["Location"] = relationship("Location", foreign_keys=[from_location_id], back_populates="outgoing_connections")
    to_location: Mapped["Location"] = relationship("Location", foreign_keys=[to_location_id], back_populates="incoming_connections")

    def __repr__(self):
        return f"<LocationConnection(from={self.from_location_id}, to={self.to_location_id}, bidirectional={self.is_bidirectional})>"