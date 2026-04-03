"""Pydantic schemas for user activity."""

# /story_app/app/schemas/user_activity.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class UserActivityBase(BaseModel):
    """Base schema for user activity data."""
    action_type: str = Field(..., description="Type of action (e.g., api_call, login, create_story)")
    action_category: Optional[str] = Field(None, description="Category of action (e.g., auth, story, world, ai)")
    action_details: Optional[str] = Field(None, description="Human-readable description of the action")
    endpoint: Optional[str] = Field(None, description="API endpoint path")
    method: Optional[str] = Field(None, description="HTTP method")
    status_code: Optional[int] = Field(None, description="HTTP response status code")
    duration_ms: Optional[float] = Field(None, description="Request duration in milliseconds")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent string")
    request_id: Optional[str] = Field(None, description="Request ID for correlation with logs")
    request_data: Optional[Dict[str, Any]] = Field(None, description="Request payload (sanitized)")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response payload (sanitized)")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    error_message: Optional[str] = Field(None, description="Error message if action failed")
    error_type: Optional[str] = Field(None, description="Type of error if action failed")

class UserActivityCreate(UserActivityBase):
    """Schema for creating a new user activity log entry."""
    user_id: Optional[int] = Field(None, description="User ID (null for anonymous users)")

class UserActivityResponse(UserActivityBase):
    """Schema for user activity response."""
    id: UUID
    user_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserActivityFilter(BaseModel):
    """Schema for filtering user activities."""
    user_id: Optional[int] = None
    action_type: Optional[str] = None
    action_category: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    has_error: Optional[bool] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

class UserActivitySummary(BaseModel):
    """Schema for user activity summary statistics."""
    total_activities: int
    unique_users: int
    total_errors: int
    average_duration_ms: Optional[float]
    most_common_actions: List[Dict[str, Any]]
    activities_by_category: Dict[str, int]
    activities_by_status: Dict[str, int]
    time_period: Dict[str, datetime]

class UserActivityBulkCreate(BaseModel):
    """Schema for bulk creating user activities (useful for batch processing)."""
    activities: List[UserActivityCreate]

class UserActivityWebSocketEvent(UserActivityBase):
    """Schema for logging WebSocket events."""
    websocket_event_type: str = Field(..., description="Type of WebSocket event (connect, disconnect, message)")
    session_id: Optional[str] = Field(None, description="WebSocket session identifier")
    message_type: Optional[str] = Field(None, description="Type of WebSocket message")
    message_size: Optional[int] = Field(None, description="Size of the message in bytes")
