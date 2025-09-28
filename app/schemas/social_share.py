"""
Pydantic schemas for social sharing tracking.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SocialShareBase(BaseModel):
    """Base schema for social share data."""
    content_type: str = Field(..., description="Type of content being shared")
    content_id: str = Field(..., description="ID of the shared content")
    content_title: Optional[str] = Field(None, description="Title of the shared content")
    content_url: str = Field(..., description="Full URL being shared")
    platform: str = Field(..., description="Social platform used for sharing")
    shared_text: Optional[str] = Field(None, description="Text content shared")
    shared_hashtags: Optional[str] = Field(None, description="Hashtags used in share")


class SocialShareCreate(SocialShareBase):
    """Schema for creating a new social share record."""
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    user_agent: Optional[str] = Field(None, description="User agent string")
    referrer: Optional[str] = Field(None, description="Referrer URL")


class SocialShareResponse(BaseModel):
    """Response schema for social share tracking."""
    success: bool = Field(..., description="Whether the share was tracked successfully")
    coin_awarded: bool = Field(..., description="Whether a coin was awarded")
    coin_amount: int = Field(..., description="Amount of coins awarded")
    daily_shares: int = Field(..., description="Total shares today")
    remaining_coin_shares: int = Field(..., description="Remaining coin-eligible shares today")
    message: str = Field(..., description="Response message")


class SocialShare(SocialShareBase):
    """Full social share schema with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    coin_awarded: bool = False
    coin_amount: int = 0
    created_at: datetime


class SocialShareDailySummaryBase(BaseModel):
    """Base schema for daily summary data."""
    date: datetime
    total_shares: int = 0
    coins_earned: int = 0
    max_coins_reached: bool = False


class SocialShareDailySummaryCreate(SocialShareDailySummaryBase):
    """Schema for creating daily summary."""
    user_id: int


class SocialShareDailySummary(SocialShareDailySummaryBase):
    """Full daily summary schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: int
    
    # Platform breakdown
    facebook_shares: int = 0
    twitter_shares: int = 0
    linkedin_shares: int = 0
    reddit_shares: int = 0
    whatsapp_shares: int = 0
    email_shares: int = 0
    copy_link_shares: int = 0
    pinterest_shares: int = 0
    telegram_shares: int = 0
    
    # Content type breakdown
    image_preview_shares: int = 0
    published_story_shares: int = 0
    ai_public_chat_shares: int = 0
    
    created_at: datetime
    updated_at: datetime


class SocialShareAnalytics(BaseModel):
    """Analytics schema for social sharing data."""
    total_shares: int = Field(..., description="Total number of shares")
    total_coins_awarded: int = Field(..., description="Total coins awarded")
    
    # Platform breakdown
    platform_stats: dict = Field(..., description="Shares by platform")
    
    # Content type breakdown
    content_type_stats: dict = Field(..., description="Shares by content type")
    
    # Time-based stats
    daily_stats: List[dict] = Field(..., description="Daily sharing statistics")
    
    # Top shared content
    top_shared_content: List[dict] = Field(..., description="Most shared content items")


class ShareUrlRequest(BaseModel):
    """Request schema for generating share URLs."""
    content_type: str = Field(..., description="Type of content being shared")
    content_id: str = Field(..., description="ID of the content")
    platform: str = Field(..., description="Target social platform")


class ShareUrlResponse(BaseModel):
    """Response schema for share URL generation."""
    share_url: str = Field(..., description="Generated share URL")
    popup_width: int = Field(..., description="Recommended popup width")
    popup_height: int = Field(..., description="Recommended popup height")