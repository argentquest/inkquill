from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AnonymousUserSessionBase(BaseModel):
    ip_address: Optional[str] = Field(None, max_length=45, description="Client IP address")
    browser_fingerprint: Optional[str] = Field(None, max_length=32, description="Browser fingerprint hash")
    user_agent: Optional[str] = Field(None, description="User agent string")

class AnonymousUserSessionCreate(AnonymousUserSessionBase):
    user_id: int
    session_token: str = Field(..., max_length=64, description="Unique session token")

class AnonymousUserSessionUpdate(BaseModel):
    last_seen_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class AnonymousUserSessionRead(AnonymousUserSessionBase):
    model_config = {"from_attributes": True}
    
    id: int
    user_id: int
    session_token: str
    created_at: datetime
    last_seen_at: datetime
    is_active: bool