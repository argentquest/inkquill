"""Pydantic schemas for world."""

# /story_app/app/schemas/world.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class WorldBase(BaseModel):
    """Base Pydantic model for a World, containing common attributes."""
    name: str = Field(..., min_length=1, max_length=255, description="The name of the world.")
    description: Optional[str] = Field(None, description="A general description of the world.")
    short_description: Optional[str] = Field(None, description="A short description of the world.")
    world_builder_data: Optional[Dict[str, Any]] = Field(None, description="JSON data from world builder wizard.")
    
    # --- FIX: Add image prompt definition ---
    image_prompt_definition: Optional[str] = Field(None, description="Text prompt for generating an image of this world.")
    # --- END FIX ---
    
    # Public access control
    is_free_chat_enabled: bool = Field(False, description="Whether this world is available for anonymous public chat.")


class WorldCreate(WorldBase):
    """Pydantic model for creating a new World. user_id will be set by the backend."""
    pass

class WorldUpdate(BaseModel):
    """Pydantic model for updating an existing World. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None)
    short_description: Optional[str] = Field(None)
    world_builder_data: Optional[Dict[str, Any]] = Field(None)
    
    # --- FIX: Add image prompt definition to update schema ---
    image_prompt_definition: Optional[str] = Field(None)
    # --- END FIX ---
    
    # Public access control
    is_free_chat_enabled: Optional[bool] = Field(None, description="Whether this world is available for anonymous public chat.")


class WorldRead(WorldBase):
    """Pydantic model for representing a World in API responses."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    # --- FIX: Add image_url to read schema ---
    image_url: Optional[str] = None
    # --- END FIX ---
    
    class Config:
        from_attributes = True
