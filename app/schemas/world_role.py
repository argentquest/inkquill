# /app/schemas/world_role.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class WorldRoleBase(BaseModel):
    name: str
    world_id: Optional[int] = None
    is_predefined: bool = False

class WorldRoleCreate(WorldRoleBase):
    pass

class WorldRoleUpdate(BaseModel):
    name: Optional[str] = None

class WorldRoleRead(WorldRoleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int