"""Pydantic schemas for story class."""

# /story_app/app/schemas/story_class.py

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import re


class StoryClassBase(BaseModel):
    """Pydantic schema for story class base."""
    name: str = Field(..., min_length=1, max_length=100, description="Short name for the story class")
    description: Optional[str] = Field(None, max_length=500, description="Description of what this class represents")
    color: str = Field(..., min_length=7, max_length=7, description="Hex color code (e.g., #FF5733)")

    @validator('color')
    def validate_hex_color(cls, v):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
        return v.upper()  # Normalize to uppercase

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()


class StoryClassCreate(StoryClassBase):
    """Pydantic schema for story class create."""
    pass


class StoryClassUpdate(BaseModel):
    """Pydantic schema for story class update."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, min_length=7, max_length=7)

    @validator('color')
    def validate_hex_color(cls, v):
        if v is not None:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('Color must be a valid hex color code (e.g., #FF5733)')
            return v.upper()
        return v

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty or just whitespace')
            return v.strip()
        return v


class StoryClass(StoryClassBase):
    """Pydantic schema for story class."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoryClassInDB(StoryClass):
    """Pydantic schema for story class in d b."""
    pass


# For use in dropdown selectors
class StoryClassOption(BaseModel):
    """Pydantic schema for story class option."""
    id: int
    name: str
    color: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
