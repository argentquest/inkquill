"""Pydantic schemas for story."""

# /story_app/app/schemas/story.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class StoryBase(BaseModel):
    """Base Pydantic model for a Story."""
    title: str = Field(..., min_length=1, max_length=255, description="The title of the story")
    short_description: Optional[str] = Field(None, description="Writer's intent and summary of the story")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary of the story")
    
    # --- FIX: Add image prompt definition ---
    image_prompt_definition: Optional[str] = Field(None, description="Text prompt for generating an image (e.g., cover art) for this story.")
    # --- END FIX ---
    
    # Story generation metadata
    story_genre: Optional[str] = Field(None, max_length=100, description="Primary genre of the story (e.g., Fantasy Adventure)")
    story_tone: Optional[str] = Field(None, max_length=100, description="Overall tone of the story (e.g., Hopeful, Dark)")
    primary_conflict_type: Optional[str] = Field(None, max_length=100, description="Main conflict type (e.g., Character vs. Self)")

class StoryCreate(StoryBase):
    """
    Pydantic model for creating a new Story.
    user_id will be added based on the authenticated user.
    world_id is optional for advanced stories - if not provided, a generic world will be created.
    """
    world_id: Optional[int] = Field(None, description="The ID of the World this story is set in. If not provided for advanced stories, a generic world will be created.")
    story_type: str = Field(default="advanced", description="Type of story: 'basic' or 'advanced'")

class StoryUpdate(BaseModel):
    """Pydantic model for updating an existing Story. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    short_description: Optional[str] = Field(None, description="Writer's intent and summary")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    world_id: Optional[int] = Field(None, description="Change the World ID for this story.")
    
    # --- FIX: Add image prompt definition to update schema ---
    image_prompt_definition: Optional[str] = Field(None)
    # --- END FIX ---
    
    # Story generation metadata
    story_genre: Optional[str] = Field(None, max_length=100)
    story_tone: Optional[str] = Field(None, max_length=100)
    primary_conflict_type: Optional[str] = Field(None, max_length=100)

class StoryRead(StoryBase):
    """
    Pydantic model for representing a Story in API responses.
    Includes core story details and metadata.
    """
    id: int
    user_id: int 
    world_id: int
    
    # Basic/Advanced story type field
    story_type: str = Field(default="advanced", description="Type of story: 'basic' or 'advanced'")
    
    created_at: datetime
    updated_at: datetime

    # --- FIX: Add image_url to read schema ---
    image_url: Optional[str] = None
    # --- END FIX ---
    
    class Config:
        from_attributes = True

# Alias for API responses
StoryResponse = StoryRead

class BasicStoryCreateResponse(StoryRead):
    """
    Response schema for Basic Story creation.
    Includes the first act ID for immediate redirection to editor.
    """
    first_act_id: int = Field(..., description="ID of the automatically created first act")
