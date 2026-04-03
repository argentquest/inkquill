"""Pydantic schemas for location."""

# /story_app/app/schemas/location.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- Optional: Import StoryRead if you plan to nest stories in LocationRead ---
# from .story import StoryRead 
# from .world import WorldRead # If you wanted to nest World in LocationRead

class LocationScaleEnum(str, Enum):
    """Enum for different scales of locations"""
    REGION = "REGION"
    CITY = "CITY"  
    BUILDING = "BUILDING"
    ROOM = "ROOM"
    AREA = "AREA"
    OBJECT = "OBJECT"
    POINT = "POINT"
    OTHER = "OTHER"

class LocationBase(BaseModel):
    """Base Pydantic model for a Location."""
    name: str = Field(..., min_length=1, max_length=255, description="The name of the location.")
    description: Optional[str] = Field(None, description="A general description of the location.")
    atmosphere: Optional[str] = Field(None, max_length=255, description="The atmosphere or general feeling of the location (e.g., Eerie, Peaceful).")
    significance: Optional[str] = Field(None, description="The general significance or role of this location within the world.")
    image_prompt_definition: Optional[str] = Field(None, description="Text prompt for generating an image of this location.")
    image_blob_path: Optional[str] = Field(None, max_length=1024, description="Path to the location's image in storage.")
    
    # AI import fields
    geography: Optional[str] = Field(None, description="Geographical features, terrain, or natural characteristics")
    cultural_context: Optional[str] = Field(None, description="Cultural, social, or political aspects of this location")
    importance_rating: Optional[int] = Field(None, ge=1, le=5, description="Significance to the story (1=minor, 5=central location)")
    connected_elements: Optional[str] = Field(None, description="Characters, locations, or lore items associated with this location")
    
    # Advanced World-Building Features
    scale: Optional[LocationScaleEnum] = Field(None, description="The scale/type of the location (for World-Builder/DM use)")
    parent_location_id: Optional[int] = Field(None, description="ID of the parent location (for hierarchy)")
    map_x: Optional[float] = Field(None, description="X coordinate on the world map")
    map_y: Optional[float] = Field(None, description="Y coordinate on the world map")
    map_z: Optional[float] = Field(None, description="Z coordinate on the world map (elevation/floor)")
    dimension_x: Optional[float] = Field(None, description="Width/length dimension")
    dimension_y: Optional[float] = Field(None, description="Height/breadth dimension")
    dimension_z: Optional[float] = Field(None, description="Depth/height dimension")
    dimension_unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement for dimensions (e.g., 'feet', 'meters', 'miles')")
    # world_id will be set by the API endpoint context or from path

class LocationCreate(LocationBase):
    """Pydantic model for creating a new Location. world_id will be contextual."""
    pass

class LocationUpdate(BaseModel):
    """Pydantic model for updating an existing Location. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    atmosphere: Optional[str] = Field(None, max_length=255)
    significance: Optional[str] = Field(None)
    image_prompt_definition: Optional[str] = Field(None)
    image_blob_path: Optional[str] = Field(None, max_length=1024)
    
    # AI import fields
    geography: Optional[str] = Field(None)
    cultural_context: Optional[str] = Field(None)
    importance_rating: Optional[int] = Field(None, ge=1, le=5)
    connected_elements: Optional[str] = Field(None)
    
    # Advanced World-Building Features
    scale: Optional[LocationScaleEnum] = Field(None)
    parent_location_id: Optional[int] = Field(None)
    map_x: Optional[float] = Field(None)
    map_y: Optional[float] = Field(None)
    map_z: Optional[float] = Field(None)
    dimension_x: Optional[float] = Field(None)
    dimension_y: Optional[float] = Field(None)
    dimension_z: Optional[float] = Field(None)
    dimension_unit: Optional[str] = Field(None, max_length=50)

class LocationRead(LocationBase):
    """Pydantic model for representing a Location in API responses."""
    id: int
    world_id: int # ID of the world this location belongs to
    
    # --- FIX: Add the image_url field ---
    image_url: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Schemas for Story-Location Association ---

class StoryLocationLinkCreate(BaseModel):
    """Schema for linking a location to a story and defining its significance in that story."""
    location_id: int
    significance_to_story: Optional[str] = Field(None, description="The location's specific significance or role in this story.")

class StoryLocationLinkRead(BaseModel):
    """Schema for reading the details of a story-location link, including the location info."""
    story_id: int
    location_id: int
    significance_to_story: Optional[str] = None
    location: LocationRead # Nested full location details

    class Config:
        from_attributes = True

class LocationInStoryRead(BaseModel):
    """Schema for listing locations associated with a story, showing their story-specific significance."""
    significance_to_story: Optional[str] = None
    # Include fields from LocationRead directly or nest LocationRead
    id: int
    name: str
    description: Optional[str] = None
    atmosphere: Optional[str] = None
    # ... other location fields you want to show in the list ...
    
    # --- FIX: Add the image_url field here as well ---
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


# --- Schemas for Location Connections ---

class LocationConnectionBase(BaseModel):
    """Base schema for location connections."""
    from_location_id: int = Field(..., description="ID of the source location")
    to_location_id: int = Field(..., description="ID of the destination location")
    path_description: Optional[str] = Field(None, description="Description of the path from source to destination")
    reverse_path_description: Optional[str] = Field(None, description="Description of the reverse path (destination to source)")
    is_bidirectional: bool = Field(True, description="Whether the connection can be traversed in both directions")
    dm_notes: Optional[str] = Field(None, description="Private notes for World-Builder/DM use")

class LocationConnectionCreate(LocationConnectionBase):
    """Schema for creating a new location connection."""
    pass

class LocationConnectionUpdate(BaseModel):
    """Schema for updating an existing location connection."""
    path_description: Optional[str] = Field(None)
    reverse_path_description: Optional[str] = Field(None)
    is_bidirectional: Optional[bool] = Field(None)
    dm_notes: Optional[str] = Field(None)

class LocationConnectionRead(LocationConnectionBase):
    """Schema for reading location connections with timestamps."""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LocationConnectionWithLocations(BaseModel):
    """Schema for location connections that includes full location details."""
    from_location_id: int
    to_location_id: int
    path_description: Optional[str] = None
    reverse_path_description: Optional[str] = None
    is_bidirectional: bool = True
    dm_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Full location objects
    from_location: LocationRead
    to_location: LocationRead

    class Config:
        from_attributes = True

