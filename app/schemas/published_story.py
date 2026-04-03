"""Pydantic schemas for published story."""

# /story_app/app/schemas/published_story.py

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

# --- PublishedStory Schemas ---

class PublishedStoryBase(BaseModel):
    """Base schema for published story data"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = True
    
class PublishedStoryCreate(PublishedStoryBase):
    """Schema for creating a published story"""
    story_id: int
    published_url: str
    filename: str
    word_count: Optional[int] = None

class PublishedStoryUpdate(BaseModel):
    """Schema for updating a published story"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None

class PublishedStoryRead(PublishedStoryBase):
    """Schema for reading a published story"""
    id: int
    story_id: int
    user_id: int
    published_url: str
    filename: str
    word_count: Optional[int]
    is_featured: bool
    view_count: int
    like_count: int
    comment_count: int
    average_rating: Optional[float]
    published_at: datetime
    updated_at: datetime
    
    # Nested data
    publisher_username: Optional[str] = None
    publisher_display_name: Optional[str] = None
    world_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PublishedStoryList(BaseModel):
    """Schema for listing published stories"""
    stories: List[PublishedStoryRead]
    total: int
    page: int
    per_page: int
    
class PublishedStoryDetail(PublishedStoryRead):
    """Schema for detailed published story view"""
    # Additional fields for detail view
    story_title: Optional[str] = None
    story_short_description: Optional[str] = None
    has_user_rated: bool = False
    user_rating: Optional[int] = None
    
# --- Comment Schemas ---

class StoryCommentBase(BaseModel):
    """Base schema for story comments"""
    content: str = Field(..., min_length=1, max_length=5000)
    
class StoryCommentCreate(StoryCommentBase):
    """Schema for creating a comment"""
    published_story_id: int
    parent_comment_id: Optional[int] = None

class StoryCommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    
class StoryCommentRead(StoryCommentBase):
    """Schema for reading a comment"""
    id: int
    published_story_id: int
    user_id: int
    parent_comment_id: Optional[int]
    is_approved: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    # Nested data
    commenter_username: str
    commenter_display_name: Optional[str]
    replies: List["StoryCommentRead"] = []
    
    model_config = ConfigDict(from_attributes=True)

# Update forward reference
StoryCommentRead.model_rebuild()

# --- Rating Schemas ---

class StoryRatingBase(BaseModel):
    """Base schema for story ratings"""
    rating: int = Field(..., ge=1, le=5)
    
class StoryRatingCreate(StoryRatingBase):
    """Schema for creating/updating a rating"""
    published_story_id: int

class StoryRatingRead(StoryRatingBase):
    """Schema for reading a rating"""
    id: int
    published_story_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class StoryRatingStats(BaseModel):
    """Schema for rating statistics"""
    average_rating: float
    total_ratings: int
    rating_distribution: dict[int, int]  # {1: count, 2: count, ..., 5: count}
