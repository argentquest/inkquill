"""
Schemas for referral tracking system.
"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class ReferralStats(BaseModel):
    """User's referral statistics."""
    total_referrals: int
    converted_referrals: int
    conversion_rate: float
    total_coins_earned: int
    today: Dict[str, int]
    platform_breakdown: Dict[str, int]
    limits: Dict[str, int]
    reward_amounts: Dict[str, int]


class ReferralHistory(BaseModel):
    """Individual referral record."""
    id: int
    referred_user_id: Optional[int]
    is_anonymous: bool
    source_platform: Optional[str]
    source_content_type: Optional[str]
    is_converted: bool
    converted_at: Optional[datetime]
    has_created_story: bool
    has_published_story: bool
    created_at: datetime


class ReferralRewardResponse(BaseModel):
    """Referral reward record."""
    id: int
    referral_id: int
    reward_type: str
    coin_amount: int
    awarded_at: datetime


class ReferralTrackingRequest(BaseModel):
    """Request to track a referral visit."""
    referral_code: str
    landing_page: Optional[str] = Field(None, description="The page where the user landed")
    referrer_url: Optional[str] = Field(None, description="The referring URL")
    user_agent: Optional[str] = Field(None, description="User agent string")
    screen_resolution: Optional[str] = Field(None, description="Screen resolution")
    viewport_size: Optional[str] = Field(None, description="Viewport size")
    timezone: Optional[str] = Field(None, description="User's timezone")
    source_platform: Optional[str] = Field(None, description="Social media or other platform")
    source_content_type: Optional[str] = Field(None, description="Type of content shared")
    source_content_id: Optional[str] = Field(None, description="ID of shared content")


class ReferralTrackingResponse(BaseModel):
    """Response from tracking a referral."""
    success: bool
    message: str
    reward_given: bool = False
    reward_amount: int = 0
    referral_id: Optional[int] = None


class ReferralCodeResponse(BaseModel):
    """Response containing user's referral code."""
    referral_code: str = Field(..., description="The referral code for this user")
    created_at: Optional[datetime] = Field(None, description="When the referral code was first used")
    usage_count: int = Field(default=0, description="How many times this code has been used")