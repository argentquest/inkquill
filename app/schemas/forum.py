"""Pydantic schemas for forum functionality."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.forum import ThreadStatus, VoteType


# Forum Category Schemas
class ForumCategoryBase(BaseModel):
    """Base schema for forum categories."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True
    icon: Optional[str] = Field(None, max_length=50)


class ForumCategoryCreate(ForumCategoryBase):
    """Schema for creating a forum category."""
    pass


class ForumCategoryUpdate(BaseModel):
    """Schema for updating a forum category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = Field(None, max_length=50)


class ForumCategoryResponse(ForumCategoryBase):
    """Schema for forum category responses."""
    id: int
    thread_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Forum Thread Schemas
class ForumThreadBase(BaseModel):
    """Base schema for forum threads."""
    title: str = Field(..., min_length=1, max_length=255)
    category_id: int
    world_id: Optional[int] = None
    story_id: Optional[int] = None


class ForumThreadCreate(ForumThreadBase):
    """Schema for creating a forum thread."""
    initial_post_content: str = Field(..., min_length=1)
    initial_post_content_html: Optional[str] = None


class ForumThreadUpdate(BaseModel):
    """Schema for updating a forum thread."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None
    status: Optional[ThreadStatus] = None


class ForumThreadListResponse(BaseModel):
    """Schema for thread list responses."""
    id: int
    title: str
    slug: str
    status: ThreadStatus
    category_id: int
    category_name: Optional[str] = None
    user_id: int
    username: str
    world_id: Optional[int] = None
    world_name: Optional[str] = None
    story_id: Optional[int] = None
    story_title: Optional[str] = None
    view_count: int
    post_count: int
    last_post_at: Optional[datetime] = None
    last_post_by_username: Optional[str] = None
    is_pinned: bool
    is_locked: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ForumThreadDetailResponse(ForumThreadListResponse):
    """Schema for detailed thread responses."""
    updated_at: datetime
    is_subscribed: Optional[bool] = False
    posts: Optional[List["ForumPostResponse"]] = []

    class Config:
        from_attributes = True


# Forum Post Schemas
class ForumPostBase(BaseModel):
    """Base schema for forum posts."""
    content: str = Field(..., min_length=1)
    content_html: Optional[str] = None
    thread_id: int
    parent_post_id: Optional[int] = None
    character_id: Optional[int] = None
    location_id: Optional[int] = None


class ForumPostCreate(ForumPostBase):
    """Schema for creating a forum post."""
    pass


class ForumPostUpdate(BaseModel):
    """Schema for updating a forum post."""
    content: Optional[str] = Field(None, min_length=1)
    content_html: Optional[str] = None


class ForumPostResponse(BaseModel):
    """Schema for forum post responses."""
    id: int
    content: str
    content_html: Optional[str] = None
    thread_id: int
    thread_title: Optional[str] = None
    user_id: int
    username: str
    user_display_name: Optional[str] = None
    parent_post_id: Optional[int] = None
    character_id: Optional[int] = None
    character_name: Optional[str] = None
    location_id: Optional[int] = None
    location_name: Optional[str] = None
    upvote_count: int
    downvote_count: int
    score: int
    user_vote: Optional[VoteType] = None
    edit_count: int
    edited_at: Optional[datetime] = None
    edited_by_username: Optional[str] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    deletion_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    replies: Optional[List["ForumPostResponse"]] = []

    class Config:
        from_attributes = True


# Vote Schemas
class ForumVoteCreate(BaseModel):
    """Schema for creating/updating a vote."""
    post_id: int
    vote_type: VoteType


class ForumVoteResponse(BaseModel):
    """Schema for vote responses."""
    post_id: int
    vote_type: VoteType
    created_at: datetime

    class Config:
        from_attributes = True


# Subscription Schemas
class ForumSubscriptionUpdate(BaseModel):
    """Schema for updating subscription preferences."""
    notify_email: Optional[bool] = None
    notify_in_app: Optional[bool] = None


class ForumSubscriptionResponse(BaseModel):
    """Schema for subscription responses."""
    thread_id: int
    thread_title: str
    notify_email: bool
    notify_in_app: bool
    created_at: datetime

    class Config:
        from_attributes = True


# User Forum Stats
class UserForumStats(BaseModel):
    """Schema for user forum statistics."""
    user_id: int
    username: str
    post_count: int
    thread_count: int
    total_karma: int
    joined_date: datetime

    class Config:
        from_attributes = True


# Allow forward references
ForumThreadDetailResponse.model_rebuild()
ForumPostResponse.model_rebuild()