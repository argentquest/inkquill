"""Pydantic schemas for world role."""

# /app/schemas/world_role.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class WorldRoleBase(BaseModel):
    """Pydantic schema for world role base."""
    name: str
    world_id: Optional[int] = None
    is_predefined: bool = False

class WorldRoleCreate(WorldRoleBase):
    """Pydantic schema for world role create."""
    pass

class WorldRoleUpdate(BaseModel):
    """Pydantic schema for world role update."""
    name: Optional[str] = None

class WorldRoleRead(WorldRoleBase):
    """Pydantic schema for world role read."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int