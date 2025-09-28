"""
Referral tracking models for user acquisition and rewards.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Referral(Base):
    """Track referral relationships and conversions."""
    
    __tablename__ = "referrals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Referrer information
    referrer_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Referred user information (nullable for anonymous users)
    referred_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    anonymous_session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Referral details
    referral_code: Mapped[str] = mapped_column(String(50), index=True)  # The numeric ID used
    source_platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # facebook, twitter, direct, etc.
    source_content_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # story, world, image, etc.
    source_content_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Tracking information
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    referral_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Conversion tracking
    is_converted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Action tracking
    has_created_story: Mapped[bool] = mapped_column(Boolean, default=False)
    has_published_story: Mapped[bool] = mapped_column(Boolean, default=False)
    first_story_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    first_publish_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_user_id], backref="referrals_made")
    referred_user = relationship("User", foreign_keys=[referred_user_id], backref="referrals_received")
    rewards = relationship("ReferralReward", back_populates="referral", cascade="all, delete-orphan")


class ReferralReward(Base):
    """Track rewards given for referrals."""
    
    __tablename__ = "referral_rewards"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Reference to the referral
    referral_id: Mapped[int] = mapped_column(Integer, ForeignKey("referrals.id", ondelete="CASCADE"), index=True)
    
    # User who received the reward (the referrer)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Reward details
    reward_type: Mapped[str] = mapped_column(String(50), index=True)  # visit, registration, first_story, first_publish
    coin_amount: Mapped[int] = mapped_column(Integer)
    
    # Tracking
    awarded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    referral = relationship("Referral", back_populates="rewards")
    user = relationship("User", backref="referral_rewards")


class ReferralLimit(Base):
    """Track daily referral reward limits per user."""
    
    __tablename__ = "referral_limits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # User tracking
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Date tracking (date only, no time)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Daily totals
    total_coins_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    # Reward type counts
    visit_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
    registration_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
    story_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
    publish_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="referral_limits")