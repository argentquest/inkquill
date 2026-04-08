"""Pydantic schemas for ai cost log."""

# /story_app/app/schemas/ai_cost_log.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class AICallLogCreate(BaseModel):
    """Pydantic schema for creating a new AI call log entry."""
    job_id: Optional[str] = None
    user_id: int
    
    # --- FIX: Make the ID optional here as well ---
    model_config_id: Optional[int] = None
    
    input_prompt: Optional[str] = None
    model_name: str
    call_type: str
    object_id: Optional[int] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    calculated_cost_usd: float
    duration_ms: Optional[int] = None

class AICallLogResponse(BaseModel):
    """Pydantic schema for AI call log response."""
    id: int
    model_name: str
    call_type: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    calculated_cost_usd: float
    created_at: datetime
    duration_ms: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
class RecentAICostResponse(BaseModel):
    """Response schema for recent AI cost summary."""
    recent_calls: List[AICallLogResponse]
    total_calls_today: int
    total_cost_today: float
    total_tokens_today: int
    last_call_time: Optional[datetime] = None

class LastAICallResponse(BaseModel):
    """Response schema for just the last AI call with coin conversion."""
    last_call: Optional[AICallLogResponse] = None
    last_call_cost_coins: int = 0
    total_calls_today: int = 0
    total_cost_coins_today: int = 0
