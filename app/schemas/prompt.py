"""Pydantic schemas for prompt."""

# /story_app/app/schemas/prompt.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# --- Core Application Imports ---
# Import the PromptTypeEnum and AgeTargetEnum from your models to ensure consistency
from app.models.prompt import PromptTypeEnum, AgeTargetEnum
# Optional: Import UserRead schema if you plan to nest user details in PromptRead
# from .user import UserRead

# --- Background: Pydantic Schemas for Prompt ---
# These models define the expected data structure for API requests (input)
# and responses (output) related to the Prompt entity. They provide
# data validation and serialization.

# --- Base Schema for Prompt (Common Fields) ---
# Not strictly necessary here as create/update have distinct optionality,
# but can be useful if many fields are shared with identical validation.
# class PromptBase(BaseModel):
#     title: str = Field(..., max_length=200, description="Title of the prompt (max 200 characters)")
#     prompt_content: str = Field(..., max_length=5000, description="The main content of the prompt (max 5000 characters)")
#     reason_to_use: Optional[str] = Field(None, description="Explanation of why or when this prompt is useful")
#     comment: Optional[str] = Field(None, description="Additional notes or comments about the prompt")
#     is_active: bool = Field(True, description="Whether the prompt is active and usable")
#     prompt_type: PromptTypeEnum = Field(..., description="The type or category of the prompt")

# --- Schema for Creating a Prompt (Input) ---
class PromptCreate(BaseModel):
    """
    Pydantic model for creating a new Prompt.
    The user_id (creator) and last_updated_by_user_id will be set by the backend
    based on the authenticated user performing the action.
    """
    title: str = Field(..., min_length=1, max_length=200, description="Title of the prompt (1-200 characters)")
    prompt_content: str = Field(..., min_length=1, max_length=5000, description="The main content of the prompt (1-5000 characters)")
    reason_to_use: Optional[str] = Field(None, description="Explanation of why or when this prompt is useful")
    comment: Optional[str] = Field(None, description="Additional notes or comments about the prompt")
    is_active: bool = Field(True, description="Whether the prompt is active and usable (defaults to True)")
    prompt_type: PromptTypeEnum = Field(..., description="The type or category of the prompt")
    age_target: AgeTargetEnum = Field(AgeTargetEnum.ALL_AGES, description="Target age group for the prompt")

# --- Schema for Updating a Prompt (Input) ---
# All fields are optional for partial updates.
class PromptUpdate(BaseModel):
    """
    Pydantic model for updating an existing Prompt.
    All fields are optional. The last_updated_by_user_id will be set by the backend.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated title of the prompt (1-200 characters)")
    prompt_content: Optional[str] = Field(None, min_length=1, max_length=5000, description="Updated main content of the prompt (1-5000 characters)")
    reason_to_use: Optional[str] = Field(None, description="Updated explanation of why or when this prompt is useful")
    comment: Optional[str] = Field(None, description="Updated additional notes or comments about the prompt")
    is_active: Optional[bool] = Field(None, description="Updated active status of the prompt")
    prompt_type: Optional[PromptTypeEnum] = Field(None, description="Updated type or category of the prompt")
    age_target: Optional[AgeTargetEnum] = Field(None, description="Updated target age group for the prompt")

# --- Schema for Reading/Returning a Prompt (Output) ---
# Defines the structure of a Prompt object when returned by the API.
class PromptRead(BaseModel):
    """
    Pydantic model for representing a Prompt in API responses.
    Includes all relevant prompt details and metadata.
    """
    id: int
    title: str
    prompt_content: str
    reason_to_use: Optional[str] = None
    comment: Optional[str] = None
    is_active: bool
    prompt_type: PromptTypeEnum # Will serialize the enum member's value (e.g., "GENERAL")
    age_target: AgeTargetEnum # Will serialize the enum member's value (e.g., "ALL_AGES")

    # Foreign key IDs for related users
    user_id: Optional[int] = None # Creator's ID (can be null if user deleted and ON DELETE SET NULL)
    last_updated_by_user_id: Optional[int] = None # ID of user who last updated

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Optional: If you want to return nested User objects for owner and last_updated_by.
    # This requires the UserRead schema to be defined and imported,
    # and SQLAlchemy relationships to be properly loaded in CRUD operations.
    # owner: Optional[UserRead] = None
    # last_updated_by: Optional[UserRead] = None

    model_config = ConfigDict(from_attributes=True)

