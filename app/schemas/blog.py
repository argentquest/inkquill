"""Blog schemas for request/response models."""
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from decimal import Decimal

from app.models.blog_post import BlogPostStatus
from app.models.blog_comment import CommentStatus


# Blog Category Schemas
class BlogCategoryBase(BaseModel):
    """Pydantic schema for blog category base."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    display_order: int = 0
    is_active: bool = True


class BlogCategoryCreate(BlogCategoryBase):
    """Pydantic schema for blog category create."""
    pass


class BlogCategoryUpdate(BaseModel):
    """Pydantic schema for blog category update."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class BlogCategoryRead(BlogCategoryBase):
    """Pydantic schema for blog category read."""
    id: int
    post_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Blog Tag Schemas
class BlogTagBase(BaseModel):
    """Pydantic schema for blog tag base."""
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class BlogTagCreate(BlogTagBase):
    """Pydantic schema for blog tag create."""
    pass


class BlogTagRead(BlogTagBase):
    """Pydantic schema for blog tag read."""
    id: int
    usage_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Blog Post Schemas
class BlogPostBase(BaseModel):
    """Pydantic schema for blog post base."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    featured_image_url: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = None
    allow_comments: bool = True
    is_ai_generated: bool = False
    is_featured: bool = False


class BlogPostCreate(BlogPostBase):
    """Pydantic schema for blog post create."""
    tags: Optional[List[str]] = Field(None, max_length=10)
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag.strip()) > 50 or not tag.strip():
                    raise ValueError('Invalid tag format')
        return v


class BlogPostUpdate(BaseModel):
    """Pydantic schema for blog post update."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    featured_image_url: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = None
    allow_comments: Optional[bool] = None
    status: Optional[BlogPostStatus] = None
    is_featured: Optional[bool] = None
    tags: Optional[List[str]] = Field(None, max_length=10)
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag.strip()) > 50 or not tag.strip():
                    raise ValueError('Invalid tag format')
        return v


class BlogPostRead(BlogPostBase):
    """Pydantic schema for blog post read."""
    id: int
    slug: str
    status: BlogPostStatus
    author_id: int
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    author: Optional['UserRead'] = None
    category: Optional[BlogCategoryRead] = None
    tags: List[BlogTagRead] = []

    model_config = ConfigDict(from_attributes=True)


class BlogPostSummary(BaseModel):
    """Lightweight blog post summary for listings."""
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    featured_image_url: Optional[str]
    author_id: int
    author_name: str
    category: Optional[BlogCategoryRead]
    tags: List[BlogTagRead]
    view_count: int
    like_count: int
    comment_count: int
    published_at: Optional[datetime]
    reading_time_minutes: int

    model_config = ConfigDict(from_attributes=True)


# Blog Comment Schemas
class BlogCommentBase(BaseModel):
    """Pydantic schema for blog comment base."""
    content: str = Field(..., min_length=1)


class BlogCommentCreate(BlogCommentBase):
    """Pydantic schema for blog comment create."""
    parent_comment_id: Optional[int] = None


class BlogCommentUpdate(BaseModel):
    """Pydantic schema for blog comment update."""
    content: Optional[str] = Field(None, min_length=1)


class BlogCommentRead(BlogCommentBase):
    """Pydantic schema for blog comment read."""
    id: int
    post_id: int
    author_id: int
    parent_comment_id: Optional[int]
    status: CommentStatus
    like_count: int
    reply_count: int
    is_author_reply: bool
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    author: Optional['UserRead'] = None
    replies: List['BlogCommentRead'] = []

    model_config = ConfigDict(from_attributes=True)


class BlogCommentWithReplies(BlogCommentRead):
    """Blog comment with nested replies for hierarchical display."""
    replies: List['BlogCommentWithReplies'] = []

    model_config = ConfigDict(from_attributes=True)


# Blog Analytics Schemas
class BlogAnalyticsRead(BaseModel):
    """Pydantic schema for blog analytics read."""
    post_id: int
    date: date
    unique_views: int
    total_views: int
    new_likes: int
    new_comments: int
    avg_read_time: int
    bounce_rate: Decimal
    social_shares: int

    model_config = ConfigDict(from_attributes=True)


class BlogAuthorStatsRead(BaseModel):
    """Pydantic schema for blog author stats read."""
    total_posts: int
    total_views: int
    total_likes: int
    follower_count: int
    avg_engagement_rate: float


# Blog Author Profile Schemas
class BlogAuthorProfileBase(BaseModel):
    """Pydantic schema for blog author profile base."""
    bio: Optional[str] = None
    profile_image_url: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = Field(None, max_length=255)
    twitter_handle: Optional[str] = Field(None, max_length=50)
    instagram_handle: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    allow_comments_default: bool = True
    auto_publish: bool = False
    email_notifications: bool = True


class BlogAuthorProfileCreate(BlogAuthorProfileBase):
    """Pydantic schema for blog author profile create."""
    pass


class BlogAuthorProfileUpdate(BlogAuthorProfileBase):
    """Pydantic schema for blog author profile update."""
    pass


class BlogAuthorProfileRead(BlogAuthorProfileBase):
    """Pydantic schema for blog author profile read."""
    id: int
    user_id: int
    total_posts: int
    total_views: int
    total_likes: int
    follower_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Import UserRead to avoid circular imports
from app.schemas.user import UserRead

# Update forward references
BlogPostRead.model_rebuild()
BlogCommentRead.model_rebuild()
BlogCommentWithReplies.model_rebuild()
