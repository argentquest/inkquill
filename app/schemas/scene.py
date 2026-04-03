"""Pydantic schemas for scene."""

# /story_app/app/schemas/scene.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Simple schema for story class in scene responses
class SceneStoryClass(BaseModel):
    """Minimal story class info for scene responses"""
    id: int
    name: str
    color: str
    
    class Config:
        from_attributes = True

# --- Background: Pydantic Schemas for Scene ---
# These models define the expected data structure for API requests (input)
# and responses (output) related to the Scene entity. They provide
# data validation and serialization for scene attributes.

# --- Base Schema for Scene (Common Fields) ---
# Contains fields that are common across create, update, and read operations.
class SceneBase(BaseModel):
    """
    Base Pydantic model for a Scene, containing common attributes.
    """
    title: Optional[str] = Field(None, max_length=255, description="A short, descriptive title for the scene.")
    summary: Optional[str] = Field(None, description="Writer's intent and summary of what happens in this scene.")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary of the scene.")
    content: Optional[str] = Field(None, description="The actual narrative content of the scene (can be HTML if using a rich text editor).")
    characters_present: Optional[str] = Field(None, description="A comma-separated list or description of characters present in the scene.")
    plot_points: Optional[str] = Field(None, description="Key events or plot developments that occur within this scene.")
    mood: Optional[str] = Field(None, max_length=100, description="The dominant mood or tone of the scene (e.g., Suspenseful, Lighthearted).")
    image_prompt_definition: Optional[str] = Field(None, description="Custom image generation prompt for this scene")
    scene_number: int = Field(..., gt=0, description="The sequential number of the scene within its parent Act (e.g., 10, 20, 30). Must be greater than 0.")
    story_class_id: Optional[int] = Field(None, description="Optional ID of a story class for color coding")


# --- Schema for Creating a Scene (Input) ---
# Used when creating a new Scene via the API.
# `act_id` will typically be a path parameter in the API endpoint.
class SceneCreate(SceneBase):
    """
    Pydantic model for creating a new Scene.
    All fields from SceneBase are used. `act_id` is expected from the path.
    The AI generation process will populate these fields.
    """
    # scene_number is required on creation.
    # Other fields are optional as they might be AI-generated and then refined.
    # However, for programmatic creation after AI generation, they would likely all be provided.
    # Making them optional here allows for flexibility if a user were to manually create a scene stub.
    pass # Inherits all fields from SceneBase, scene_number is already required there.


# --- Schema for Updating a Scene (Input) ---
# All fields are optional for partial updates.
class SceneUpdate(BaseModel):
    """
    Pydantic model for updating an existing Scene.
    All fields are optional, allowing for partial updates.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated title of the scene.")
    summary: Optional[str] = Field(None, description="Updated writer's intent and summary of the scene.")
    ai_summary: Optional[str] = Field(None, description="Updated AI-generated summary of the scene.")
    content: Optional[str] = Field(None, description="Updated narrative content of the scene.")
    characters_present: Optional[str] = Field(None, description="Updated list/description of characters present.")
    plot_points: Optional[str] = Field(None, description="Updated key events or plot points.")
    mood: Optional[str] = Field(None, max_length=100, description="Updated mood or tone of the scene.")
    image_prompt_definition: Optional[str] = Field(None, description="Updated custom image generation prompt for this scene")
    scene_number: Optional[int] = Field(None, gt=0, description="Updated sequential number of the scene (must be > 0).")
    story_class_id: Optional[int] = Field(None, description="Updated ID of the story class for color coding (can be null to remove)")


# --- Schema for Reading/Returning a Scene (Output) ---
# Defines the structure of a Scene object when returned by the API.
class SceneRead(SceneBase):
    """
    Pydantic model for representing a Scene in API responses.
    Includes all core scene details and metadata.
    """
    id: int
    act_id: int # The ID of the parent Act

    created_at: datetime
    updated_at: datetime
    
    # Include story class information if available
    story_class: Optional[SceneStoryClass] = None
    
    # Image URL field for displaying current image
    image_url: Optional[str] = None

    class Config:
        # Enables compatibility with ORM models (SQLAlchemy).
        # Allows Pydantic to automatically map data from ORM object attributes.
        from_attributes = True # Replaces orm_mode = True in Pydantic v1

