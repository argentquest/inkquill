"""Pydantic schemas for ai model config."""

# /story_app/app/schemas/ai_model_config.py
from pydantic import BaseModel
from typing import Optional

# These imports are correct because they point to a different module.
from app.models.ai_model_config import AIProviderEnum, AIModelTypeEnum

# The erroneous self-import "from app.schemas.ai_model_config import AIModelConfigurationRead" has been REMOVED.

class AIModelConfigurationRead(BaseModel):
    """
    Pydantic schema for returning available AI model configurations to the frontend.
    Excludes sensitive cost data and detailed parameters not needed by the UI.
    """
    id: int
    display_name: str
    description: Optional[str] = None
    
    # We send the actual model_name so the frontend can, if it wants,
    # show the underlying engine (e.g., "gpt-4o").
    model_name: str
    is_public_chat_default: Optional[bool] = None 

    class Config:
        from_attributes = True
        use_enum_values = True # Ensures enum members are returned as strings
