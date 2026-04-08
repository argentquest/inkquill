"""Pydantic schemas for llm models."""

# /story_app/app/schemas/llm_models.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.models.ai_model_config import AIProviderEnum, AIModelTypeEnum


class LLMModelRead(BaseModel):
    """Schema for reading LLM model configuration"""
    id: int
    display_name: str
    model_name: str
    description: Optional[str] = None
    provider: AIProviderEnum
    model_type: AIModelTypeEnum
    is_active: bool
    is_public_chat_default: Optional[bool] = None
    max_tokens: int
    temperature: float
    top_p: float
    presence_penalty: float
    frequency_penalty: float
    is_json_mode: bool
    provider_cost_input_usd_pm: float
    provider_cost_output_usd_pm: float
    user_price_input_usd_pm: float
    user_price_output_usd_pm: float
    
    model_config = ConfigDict(from_attributes=True)
class LLMModelsResponse(BaseModel):
    """Response containing list of LLM models with metadata"""
    models: list[LLMModelRead]
    total_count: int
    active_count: int
    providers: list[str]
