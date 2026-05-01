"""Pydantic schemas for standalone chatbot sessions and messages."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ChatbotMessageRead(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    model_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatbotSessionRead(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatbotSessionWithMessages(ChatbotSessionRead):
    messages: List[ChatbotMessageRead] = []


class ChatbotSessionCreate(BaseModel):
    title: str = Field(default="New conversation", max_length=255)


class ChatbotSessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ChatbotSendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)


class ChatbotSendMessageResponse(BaseModel):
    user_message: ChatbotMessageRead
    ai_message: ChatbotMessageRead
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    model_name: Optional[str] = None
