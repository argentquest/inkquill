# /ai_rag_story_app/app/schemas/ai_text_transform.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class AITextTransformRequest(BaseModel):
    """Request schema for AI text transformation"""
    text: str = Field(..., description="The selected text to transform")
    operation_id: int = Field(..., description="ID of the QuickAI prompt to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the transformation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The cat sat on the mat.",
                "operation_id": 1,
                "context": {
                    "document_type": "scene",
                    "document_id": "123",
                    "full_content": "Chapter 1: The beginning...",
                    "metadata": {
                        "story_title": "My Story",
                        "act_title": "Act 1",
                        "scene_title": "Opening Scene"
                    }
                }
            }
        }

class AITextTransformResponse(BaseModel):
    """Response schema for AI text transformation"""
    success: bool = Field(..., description="Whether the transformation was successful")
    transformed_text: str = Field(..., description="The transformed text")
    original_text: str = Field(..., description="The original text for reference")
    operation_used: str = Field(..., description="Name of the operation used")
    tokens_used: int = Field(..., description="Number of tokens consumed")
    cost_estimate: float = Field(..., description="Estimated cost in USD")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "transformed_text": "The sleek black cat gracefully settled upon the well-worn woven mat.",
                "original_text": "The cat sat on the mat.",
                "operation_used": "Expand with Details",
                "tokens_used": 45,
                "cost_estimate": 0.0023,
                "processing_time": 1.2
            }
        }

class AITextCostEstimateRequest(BaseModel):
    """Request schema for cost estimation"""
    text: str = Field(..., description="The text to estimate cost for")
    operation_id: int = Field(..., description="ID of the QuickAI prompt to use")
    
class AITextCostEstimateResponse(BaseModel):
    """Response schema for cost estimation"""
    estimated_tokens: int = Field(..., description="Estimated token usage")
    estimated_cost: float = Field(..., description="Estimated cost in USD")
    operation_name: str = Field(..., description="Name of the operation")

class QuickAIOperation(BaseModel):
    """Schema for QuickAI operations"""
    id: int = Field(..., description="Operation ID")
    title: str = Field(..., description="Display name of the operation")
    description: Optional[str] = Field(None, description="Description of what this operation does")
    icon: Optional[str] = Field(None, description="FontAwesome icon class")
    is_active: bool = Field(True, description="Whether this operation is available")
    created_at: datetime = Field(..., description="When this operation was created")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Rewrite for Clarity",
                "description": "Improves readability and clarity",
                "icon": "fas fa-edit",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class QuickAIOperationsResponse(BaseModel):
    """Response schema for available operations"""
    operations: List[QuickAIOperation] = Field(..., description="List of available QuickAI operations")
    total_count: int = Field(..., description="Total number of operations")
    
class AITextTransformError(BaseModel):
    """Error response schema"""
    success: bool = Field(False, description="Always false for error responses")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_type": "RATE_LIMIT_EXCEEDED",
                "error_message": "You have exceeded the rate limit for AI transformations. Please try again in a few minutes.",
                "error_code": "RATE_LIMIT_429"
            }
        }