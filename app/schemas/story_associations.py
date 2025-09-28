# /app/schemas/story_associations.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Story-Character Association Schemas
class StoryCharacterAssociationBase(BaseModel):
    story_id: int
    character_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class StoryCharacterAssociationCreate(StoryCharacterAssociationBase):
    pass

class StoryCharacterAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class StoryCharacterAssociationRead(StoryCharacterAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Story-Location Association Schemas
class StoryLocationAssociationBase(BaseModel):
    story_id: int
    location_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class StoryLocationAssociationCreate(StoryLocationAssociationBase):
    pass

class StoryLocationAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class StoryLocationAssociationRead(StoryLocationAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Story-LoreItem Association Schemas
class StoryLoreItemAssociationBase(BaseModel):
    story_id: int
    lore_item_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class StoryLoreItemAssociationCreate(StoryLoreItemAssociationBase):
    pass

class StoryLoreItemAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class StoryLoreItemAssociationRead(StoryLoreItemAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int