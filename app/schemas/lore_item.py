"""Pydantic schemas for lore item."""

# /story_app/app/schemas/lore_item.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Import the Enum from the model to ensure consistency
from app.models.lore_item import LoreItemCategoryEnum

class LoreItemBase(BaseModel):
    """Base Pydantic model for a Lore Item."""
    title: str = Field(..., min_length=1, max_length=255, description="The title or name of the lore item.")
    description: Optional[str] = Field(None, description="A detailed description of the lore item.")
    category: LoreItemCategoryEnum = Field(..., description="The category of the lore item (e.g., Magic System, Historical Event).")
    image_prompt_definition: Optional[str] = Field(None, description="Text prompt for generating an image related to this lore item.")
    image_blob_path: Optional[str] = Field(None, max_length=1024, description="Path to the lore item's image in storage.")
    
    current_location_id: Optional[int] = Field(None, description="ID of the location where this lore item is currently placed")
    placement_note: Optional[str] = Field(None, description="Description of how/where the lore item is placed at the location")
    
    # AI import fields
    importance_rating: Optional[int] = Field(None, ge=1, le=5, description="Significance to the story (1=minor, 5=central concept)")
    related_elements: Optional[str] = Field(None, description="Characters, locations, or other lore items this element connects to")

class LoreItemCreate(LoreItemBase):
    """Pydantic model for creating a new Lore Item. world_id will be contextual."""
    pass

class LoreItemUpdate(BaseModel):
    """Pydantic model for updating an existing Lore Item. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    category: Optional[LoreItemCategoryEnum] = Field(None)
    image_prompt_definition: Optional[str] = Field(None)
    image_blob_path: Optional[str] = Field(None, max_length=1024)
    importance_rating: Optional[int] = Field(None, ge=1, le=5)
    related_elements: Optional[str] = Field(None)
    
    current_location_id: Optional[int] = Field(None)
    placement_note: Optional[str] = Field(None)

class LoreItemRead(LoreItemBase):
    """Pydantic model for representing a Lore Item in API responses."""
    id: int
    world_id: int 

    # --- FIX: Add the missing image_url field ---
    image_url: Optional[str] = None
    # --- END FIX ---

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True

# --- Schemas for Story-LoreItem Association ---

class StoryLoreItemLinkCreate(BaseModel):
    """Schema for linking a lore item to a story and defining its relevance to that story."""
    lore_item_id: int
    relevance_to_story: Optional[str] = Field(None, description="How this lore item is relevant or impacts this specific story.")

class StoryLoreItemLinkRead(BaseModel):
    """Schema for reading the details of a story-lore item link, including the lore item info."""
    story_id: int
    lore_item_id: int
    relevance_to_story: Optional[str] = None
    lore_item: LoreItemRead 

    class Config:
        from_attributes = True

class LoreItemInStoryRead(BaseModel):
    """Schema for listing lore items associated with a story, showing their story-specific relevance."""
    relevance_to_story: Optional[str] = None
    id: int
    title: str
    category: LoreItemCategoryEnum
    description: Optional[str] = None
    
    # --- FIX: Add the missing image_url field here as well ---
    image_url: Optional[str] = None
    # --- END FIX ---

    class Config:
        from_attributes = True
        use_enum_values = True

