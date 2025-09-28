# /ai_rag_story_app/app/schemas/chat.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# --- Chat Session Schemas ---

class ChatSessionBase(BaseModel):
    """Base schema for ChatSession"""
    title: str = Field(..., max_length=255, description="Title of the chat session")


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new chat session"""
    world_id: int = Field(..., description="ID of the world this session is about")


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session"""
    title: Optional[str] = Field(None, max_length=255, description="Updated title")


class ChatSessionRead(ChatSessionBase):
    """Schema for reading a chat session"""
    id: int
    world_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# --- Chat Message Schemas ---

class ChatMessageBase(BaseModel):
    """Base schema for ChatMessage"""
    role: str = Field(..., description="Role of the message sender ('user' or 'assistant')")
    content: str = Field(..., description="Content of the message")
    element_type: Optional[str] = Field(None, max_length=50, description="Type of element if targeting specific element")
    element_id: Optional[int] = Field(None, description="ID of the element if targeting specific element")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message"""
    full_context: Optional[Dict[str, Any]] = Field(None, description="Complete context sent to AI")


class ChatMessageRead(ChatMessageBase):
    """Schema for reading a chat message"""
    id: int
    session_id: int
    full_context: Optional[Dict[str, Any]]
    cost_log_id: Optional[int]
    created_at: datetime
    rag_sources: Optional[List[Dict[str, Any]]] = Field(None, description="RAG sources used for this response")
    
    class Config:
        from_attributes = True
    
    @property
    def sources(self) -> List[Dict[str, Any]]:
        """Extract RAG sources from full_context if available"""
        if self.full_context and 'rag_sources' in self.full_context:
            return self.full_context['rag_sources']
        return []


# --- Combined Schemas ---

class ChatSessionWithMessages(ChatSessionRead):
    """Chat session with its messages"""
    messages: List[ChatMessageRead] = []


# --- Request/Response Schemas ---

class SendMessageRequest(BaseModel):
    """Request schema for sending a chat message"""
    message: str = Field(..., description="The user's message")
    element_type: Optional[str] = Field(None, description="Type of element to target")
    element_id: Optional[int] = Field(None, description="ID of element to target")
    ai_model_config_id: Optional[int] = Field(None, description="AI model configuration to use")


class AICallStats(BaseModel):
    """Schema for AI call statistics"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    model_name: str
    duration_ms: int

class SendMessageResponse(BaseModel):
    """Response schema for sending a chat message"""
    user_message: ChatMessageRead
    ai_response: ChatMessageRead
    session_updated_at: datetime
    call_stats: Optional[AICallStats] = None


class WorldContextData(BaseModel):
    """Schema for world context data"""
    world: Dict[str, Any]
    characters: List[Dict[str, Any]]
    locations: List[Dict[str, Any]]
    lore_items: List[Dict[str, Any]]
    stories: List[Dict[str, Any]]
    acts: List[Dict[str, Any]]
    scenes: List[Dict[str, Any]]


class ChatSessionListResponse(BaseModel):
    """Response schema for listing chat sessions"""
    sessions: List[ChatSessionRead]
    total: int