"""Pydantic schemas for act associations."""

# /app/schemas/act_associations.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Act-Character Association Schemas
class ActCharacterAssociationBase(BaseModel):
    """Pydantic schema for act character association base."""
    act_id: int
    character_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class ActCharacterAssociationCreate(ActCharacterAssociationBase):
    """Pydantic schema for act character association create."""
    pass

class ActCharacterAssociationUpdate(BaseModel):
    """Pydantic schema for act character association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class ActCharacterAssociationRead(ActCharacterAssociationBase):
    """Pydantic schema for act character association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Act-Location Association Schemas
class ActLocationAssociationBase(BaseModel):
    """Pydantic schema for act location association base."""
    act_id: int
    location_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class ActLocationAssociationCreate(ActLocationAssociationBase):
    """Pydantic schema for act location association create."""
    pass

class ActLocationAssociationUpdate(BaseModel):
    """Pydantic schema for act location association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class ActLocationAssociationRead(ActLocationAssociationBase):
    """Pydantic schema for act location association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Act-LoreItem Association Schemas
class ActLoreItemAssociationBase(BaseModel):
    """Pydantic schema for act lore item association base."""
    act_id: int
    lore_item_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class ActLoreItemAssociationCreate(ActLoreItemAssociationBase):
    """Pydantic schema for act lore item association create."""
    pass

class ActLoreItemAssociationUpdate(BaseModel):
    """Pydantic schema for act lore item association update."""
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class ActLoreItemAssociationRead(ActLoreItemAssociationBase):
    """Pydantic schema for act lore item association read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int