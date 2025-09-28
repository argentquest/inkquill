# /ai_rag_story_app/app/schemas/story_generation.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class StoryGenerationRequest(BaseModel):
    """Request model for generating a new story from world elements."""
    selected_characters: List[int] = Field(..., description="Character IDs to include")
    selected_locations: List[int] = Field(..., description="Location IDs to include")
    selected_lore_items: List[int] = Field(..., description="Lore item IDs to include")
    story_genre: str = Field(..., max_length=100, description="Selected story genre")
    story_tone: str = Field(..., max_length=100, description="Selected story tone")
    primary_conflict_type: str = Field(..., max_length=100, description="Selected conflict type")
    ai_model_config_id: int = Field(..., description="ID of the AI model configuration to use")
    author_concept: Optional[str] = Field(None, max_length=200, description="Optional author concept or story idea")


class StoryGenerationResponse(BaseModel):
    """Response model for story generation."""
    success: bool
    story_id: Optional[int] = None
    generated_outline: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    partial_data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None