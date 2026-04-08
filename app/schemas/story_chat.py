"""Pydantic schemas for story chat."""

# /story_app/app/schemas/story_chat.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Story Chat Message Schemas ---

class StoryChatMessageCreate(BaseModel):
    """Schema for creating a story chat message"""
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    target_element: Optional[str] = Field(None, description="Target story element type (act, scene, character, etc.)")
    target_element_id: Optional[int] = Field(None, description="ID of target story element")

class StoryChatMessageRead(BaseModel):
    """Schema for reading a story chat message"""
    id: int
    session_id: int
    role: str  # 'user' or 'assistant'
    content: str
    target_element: Optional[str] = None
    target_element_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class StoryChatSessionCreate(BaseModel):
    """Schema for creating a story chat session"""
    title: str = Field(..., min_length=1, max_length=255, description="Session title")
    description: Optional[str] = Field(None, max_length=1000, description="Session description")
    focus_area: Optional[str] = Field(None, description="Focus area (plot, characters, world, general, etc.)")

class StoryChatSessionUpdate(BaseModel):
    """Schema for updating a story chat session"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    focus_area: Optional[str] = Field(None)

class StoryChatSessionRead(BaseModel):
    """Schema for reading a story chat session"""
    id: int
    story_id: int
    user_id: int
    title: str
    description: Optional[str] = None
    focus_area: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
class StoryChatSessionWithMessages(StoryChatSessionRead):
    """Schema for reading a story chat session with its messages"""
    messages: List[StoryChatMessageRead] = []

# --- Request/Response Schemas ---

class SendStoryChatMessageRequest(BaseModel):
    """Schema for sending a message in a story chat session"""
    message: str = Field(..., min_length=1, max_length=10000, description="Message content")
    target_element: Optional[str] = Field(None, description="Target story element type")
    target_element_id: Optional[int] = Field(None, description="ID of target story element")
    streaming: bool = Field(True, description="Whether to stream the response")

class SendStoryChatMessageResponse(BaseModel):
    """Schema for story chat message response"""
    message_id: int
    response: str
    ai_call_stats: Optional[Dict[str, Any]] = None
    context_used: Optional[Dict[str, Any]] = None

# --- Story Context Schemas ---

class StoryContextSummary(BaseModel):
    """Schema for story context information used in chat"""
    story_id: int
    story_title: str
    story_type: str  # 'basic' or 'advanced'
    acts_count: int
    scenes_count: int
    characters_count: int = 0
    locations_count: int = 0
    world_context: Optional[Dict[str, Any]] = None

class StoryChatStats(BaseModel):
    """Schema for story chat session statistics"""
    total_sessions: int
    total_messages: int
    most_active_focus_area: Optional[str] = None
    recent_activity: datetime
