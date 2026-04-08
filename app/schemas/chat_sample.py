"""Pydantic schemas for chat sample."""

# /mnt/c/Code2025/rag/app/schemas/chat_sample.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ChatSampleBase(BaseModel):
    """Base schema for chat samples"""
    title: str
    prompt_text: str
    category: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class ChatSampleCreate(ChatSampleBase):
    """Schema for creating a chat sample"""
    pass


class ChatSampleUpdate(BaseModel):
    """Schema for updating a chat sample"""
    title: Optional[str] = None
    prompt_text: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class ChatSampleRead(ChatSampleBase):
    """Schema for reading a chat sample"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
