# /app/schemas/act_associations.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Act-Character Association Schemas
class ActCharacterAssociationBase(BaseModel):
    act_id: int
    character_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class ActCharacterAssociationCreate(ActCharacterAssociationBase):
    pass

class ActCharacterAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class ActCharacterAssociationRead(ActCharacterAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Act-Location Association Schemas
class ActLocationAssociationBase(BaseModel):
    act_id: int
    location_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class ActLocationAssociationCreate(ActLocationAssociationBase):
    pass

class ActLocationAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class ActLocationAssociationRead(ActLocationAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Act-LoreItem Association Schemas
class ActLoreItemAssociationBase(BaseModel):
    act_id: int
    lore_item_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class ActLoreItemAssociationCreate(ActLoreItemAssociationBase):
    pass

class ActLoreItemAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class ActLoreItemAssociationRead(ActLoreItemAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int