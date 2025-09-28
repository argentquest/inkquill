# /ai_rag_story_app/app/schemas/act.py

from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from datetime import datetime

# --- Core Application Imports ---
# Optional: If you decide to nest the PromptRead schema for system_prompt
# from .prompt import PromptRead

if TYPE_CHECKING:
    from .story_class import StoryClassOption 

# --- Background: Pydantic Schemas for Act ---
# This file defines the Pydantic models for the Act entity. These schemas are used
# by FastAPI for validating incoming request data when creating or updating Acts,
# and for serializing Act data when returning it in API responses. They now include
# fields for act_summary, writer_notes, and system_prompt_id.

# --- Schema for Creating an Act (Input) ---
# Defines the fields required/allowed when creating a new Act via the API.
# The `story_id` is typically obtained from the URL path parameter.
class ActCreate(BaseModel):
    """
    Pydantic model for creating a new Act.
    Requires a title and an act_number. Other fields are optional.
    """
    title: str = Field(..., min_length=1, max_length=255, description="The title of the act")
    description: Optional[str] = Field(None, description="The main description or content of the act")
    act_number: int = Field(..., gt=0, description="The sequential number of the act within the story (must be > 0)")
    
    # New optional fields
    act_summary: Optional[str] = Field(None, description="Writer's intent and summary of the act's content or purpose")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary of the act")
    writer_notes: Optional[str] = Field(None, description="Private notes for the writer regarding this act")
    image_prompt_definition: Optional[str] = Field(None, description="Custom image generation prompt for this act")
    system_prompt_id: Optional[int] = Field(None, description="Optional ID of a system prompt to associate with this act")
    story_class_id: Optional[int] = Field(None, description="Optional ID of a story class for color coding")

# --- Schema for Updating an Act (Input) ---
# Defines the fields that can be updated for an existing Act. All fields are optional.
class ActUpdate(BaseModel):
    """
    Pydantic model for updating an existing Act.
    All fields are optional, allowing partial updates.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated title of the act")
    description: Optional[str] = Field(None, description="Updated main description or content of the act")
    act_number: Optional[int] = Field(None, gt=0, description="Updated sequential number of the act (must be > 0)")

    # New optional fields for update
    act_summary: Optional[str] = Field(None, description="Updated writer's intent and summary of the act")
    ai_summary: Optional[str] = Field(None, description="Updated AI-generated summary of the act")
    writer_notes: Optional[str] = Field(None, description="Updated writer's notes for this act")
    image_prompt_definition: Optional[str] = Field(None, description="Updated custom image generation prompt for this act")
    current_image_id: Optional[int] = Field(None, description="Updated ID of the current image for this act (can be null to remove)")
    system_prompt_id: Optional[int] = Field(None, description="Updated ID of the system prompt for this act (can be null to remove)")
    story_class_id: Optional[int] = Field(None, description="Updated ID of the story class for color coding (can be null to remove)")
    # Note: If system_prompt_id is set to null explicitly, the FK should be cleared.
    # If you want to ensure it's always an int or None, Pydantic handles that.

# --- Schema for Reading/Returning an Act (Output) ---
# Defines the structure of an Act object when returned by the API.
# Includes database-generated fields like id, story_id, and timestamps, plus the new fields.
class ActRead(BaseModel):
    """
    Pydantic model for representing an Act in API responses.
    Includes all core act details, new fields, and metadata.
    """
    id: int
    title: str
    description: Optional[str] = None
    act_number: int
    story_id: int # Include the parent story ID for context

    # New fields in the response
    act_summary: Optional[str] = None
    ai_summary: Optional[str] = None
    writer_notes: Optional[str] = None
    image_prompt_definition: Optional[str] = None
    current_image_id: Optional[int] = None
    system_prompt_id: Optional[int] = None
    story_class_id: Optional[int] = None
    
    # Image URL field for displaying current image
    image_url: Optional[str] = None

    # Optional: If you want to return the full System Prompt object when reading an Act
    # This would require eager loading in the CRUD operation and a PromptRead schema.
    # system_prompt: Optional[PromptRead] = None 

    created_at: datetime
    updated_at: datetime

    # Include nested story class information if available
    # story_class: Optional['StoryClassOption'] = None  # Removed to fix Pydantic forward reference issue

    class Config:
        # Enable ORM mode for compatibility with SQLAlchemy models.
        from_attributes = True # Replaces orm_mode = True in Pydantic v1
