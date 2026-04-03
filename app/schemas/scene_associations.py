"""Pydantic schemas for scene associations."""

# /app/schemas/scene_associations.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Scene-Character Association Schemas
class SceneCharacterAssociationBase(BaseModel):
    """Pydantic schema for scene character association base."""
    scene_id: int
    character_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class SceneCharacterAssociationCreate(SceneCharacterAssociationBase):
    """Pydantic schema for scene character association create."""
    pass

class SceneCharacterAssociationUpdate(BaseModel):
    """Pydantic schema for scene character association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class SceneCharacterAssociationRead(SceneCharacterAssociationBase):
    """Pydantic schema for scene character association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Scene-Location Association Schemas
class SceneLocationAssociationBase(BaseModel):
    """Pydantic schema for scene location association base."""
    scene_id: int
    location_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class SceneLocationAssociationCreate(SceneLocationAssociationBase):
    """Pydantic schema for scene location association create."""
    pass

class SceneLocationAssociationUpdate(BaseModel):
    """Pydantic schema for scene location association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class SceneLocationAssociationRead(SceneLocationAssociationBase):
    """Pydantic schema for scene location association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Scene-LoreItem Association Schemas
class SceneLoreItemAssociationBase(BaseModel):
    """Pydantic schema for scene lore item association base."""
    scene_id: int
    lore_item_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class SceneLoreItemAssociationCreate(SceneLoreItemAssociationBase):
    """Pydantic schema for scene lore item association create."""
    pass

class SceneLoreItemAssociationUpdate(BaseModel):
    """Pydantic schema for scene lore item association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class SceneLoreItemAssociationRead(SceneLoreItemAssociationBase):
    """Pydantic schema for scene lore item association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int