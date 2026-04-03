"""Pydantic schemas for story associations."""

# /app/schemas/story_associations.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Story-Character Association Schemas
class StoryCharacterAssociationBase(BaseModel):
    """Pydantic schema for story character association base."""
    story_id: int
    character_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class StoryCharacterAssociationCreate(StoryCharacterAssociationBase):
    """Pydantic schema for story character association create."""
    pass

class StoryCharacterAssociationUpdate(BaseModel):
    """Pydantic schema for story character association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class StoryCharacterAssociationRead(StoryCharacterAssociationBase):
    """Pydantic schema for story character association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Story-Location Association Schemas
class StoryLocationAssociationBase(BaseModel):
    """Pydantic schema for story location association base."""
    story_id: int
    location_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class StoryLocationAssociationCreate(StoryLocationAssociationBase):
    """Pydantic schema for story location association create."""
    pass

class StoryLocationAssociationUpdate(BaseModel):
    """Pydantic schema for story location association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class StoryLocationAssociationRead(StoryLocationAssociationBase):
    """Pydantic schema for story location association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Story-LoreItem Association Schemas
class StoryLoreItemAssociationBase(BaseModel):
    """Pydantic schema for story lore item association base."""
    story_id: int
    lore_item_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class StoryLoreItemAssociationCreate(StoryLoreItemAssociationBase):
    """Pydantic schema for story lore item association create."""
    pass

class StoryLoreItemAssociationUpdate(BaseModel):
    """Pydantic schema for story lore item association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class StoryLoreItemAssociationRead(StoryLoreItemAssociationBase):
    """Pydantic schema for story lore item association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int