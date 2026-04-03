"""Pydantic schemas for base."""

# /story_app/app/schemas/base.py
# Base schemas for API responses (ApiResponse) and errors (ApiError).

from pydantic import BaseModel, Field
from typing import TypeVar, Optional, List, Union, Dict, Any

T = TypeVar('T')

class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""
    total: int = Field(..., description="Total number of items available.")
    page: int = Field(..., description="Current page number (1-indexed).")
    per_page: int = Field(..., description="Number of items per page.")
    pages: int = Field(..., description="Total number of pages available.")

class ApiMeta(BaseModel):
    """Meta information that can accompany an API response."""
    page: Optional[int] = Field(None, description="Current page number.")
    limit: Optional[int] = Field(None, description="Items per page.")
    total: Optional[int] = Field(None, description="Total number of items.")
    pages: Optional[int] = Field(None, description="Total number of pages.")

class ApiError(BaseModel):
    """Standardized error response schema."""
    code: str = Field(..., description="Error code identifier.")
    message: str = Field(..., description="Human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details.")

class ApiResponse(BaseModel):
    """Standardized API response schema."""
    success: bool = Field(..., description="Indicates if the operation was successful.")
    data: Optional[Any] = Field(None, description="The main response data (can be any type).")
    errors: Optional[List[ApiError]] = Field(None, description="List of errors (only present if success is False).")
    meta: Optional[ApiMeta] = Field(None, description="Optional meta information.")

    model_config = {
        "arbitrary_types_allowed": True
    }

    @classmethod
    def success_response(cls, data: Any = None, meta: ApiMeta = None) -> "ApiResponse":
        """Factory method for successful responses."""
        return cls(success=True, data=data, meta=meta)

    @classmethod
    def error_response(cls, errors: List[ApiError], meta: ApiMeta = None) -> "ApiResponse":
        """Factory method for error responses."""
        return cls(success=False, errors=errors, meta=meta)

