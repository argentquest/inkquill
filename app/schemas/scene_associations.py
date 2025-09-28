# /app/schemas/scene_associations.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Scene-Character Association Schemas
class SceneCharacterAssociationBase(BaseModel):
    scene_id: int
    character_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class SceneCharacterAssociationCreate(SceneCharacterAssociationBase):
    pass

class SceneCharacterAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class SceneCharacterAssociationRead(SceneCharacterAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Scene-Location Association Schemas
class SceneLocationAssociationBase(BaseModel):
    scene_id: int
    location_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class SceneLocationAssociationCreate(SceneLocationAssociationBase):
    pass

class SceneLocationAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class SceneLocationAssociationRead(SceneLocationAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

# Scene-LoreItem Association Schemas
class SceneLoreItemAssociationBase(BaseModel):
    scene_id: int
    lore_item_id: int
    roles: List[str] = []
    notes: Optional[str] = None

class SceneLoreItemAssociationCreate(SceneLoreItemAssociationBase):
    pass

class SceneLoreItemAssociationUpdate(BaseModel):
    roles: Optional[List[str]] = None
    notes: Optional[str] = None

class SceneLoreItemAssociationRead(SceneLoreItemAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int