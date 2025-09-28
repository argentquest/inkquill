# /ai_rag_story_app/app/models/user.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List, Optional, TYPE_CHECKING

# --- Core Application Imports ---
from app.db.database import Base 

if TYPE_CHECKING:
    from .story import Story
    from .uploaded_document import UploadedDocument
    from .prompt import Prompt
    from .world import World
    from .chat_session import ChatSession
    from .forum import ForumThread, ForumPost, ForumVote, ForumSubscription
    from .user_account import UserAccount
    from .anonymous_user_session import AnonymousUserSession
    from .published_story import PublishedStory
    from .story_comment import StoryComment
    from .story_rating import StoryRating
    from .user_activity import UserActivity
    from .social_share import SocialShare, SocialShareDailySummary
    from .story_chat_session import StoryChatSession
    from .user_interview_response import UserInterviewResponse
    from .brainstorm_session import BrainstormSession, BrainstormFavorite, BrainstormStory
    from .blog_post import BlogPost
    from .blog_comment import BlogComment
    from .blog_like import BlogLike
    from .blog_follow import BlogFollow
    from .blog_view import BlogView
    from .blog_author_profile import BlogAuthorProfile
    from .blog_subscription import BlogSubscription 

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True) 
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)  # Allow NULL for OAuth users
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # OAuth fields
    auth_provider: Mapped[str] = mapped_column(String(50), default='local', nullable=False)
    provider_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    provider_data: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # --- CORRECTED: Default is_active to False ---
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # --- END CORRECTION ---
    
    # Admin flag for users with administrative privileges
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    
    # Welcome interview data and analysis
    interview_data: Mapped[Optional[dict]] = mapped_column(JSON, default=None, nullable=True)
    
    # Bonus reward tracking (for onboarding and achievements)
    bonus1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Step 1: Intro Interview (150 coins)
    bonus2: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Step 2: Story Brainstorm (50 coins)
    bonus3: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Step 3: Start Writing (50 coins)
    bonus4: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Future bonus
    bonus5: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Future bonus
    bonus6: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Future bonus
    bonus7: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Future bonus
    bonus8: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Future bonus
    bonus9: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Future bonus
    bonus10: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # Future bonus

    # Referral tracking
    referred_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Count of successful referrals

    # Password reset tracking
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expires: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    created_stories: Mapped[List["Story"]] = relationship(
        "Story",
        foreign_keys="[Story.user_id]", 
        back_populates="OwnerUser",
        cascade="all, delete-orphan" 
    )

    uploaded_documents: Mapped[List["UploadedDocument"]] = relationship(
        "UploadedDocument",
        back_populates="owner",
        cascade="all, delete-orphan" 
    )

    prompts: Mapped[List["Prompt"]] = relationship(
        "Prompt",
        foreign_keys="[Prompt.user_id]", 
        back_populates="owner"
        # No cascade on prompts based on previous setup for ON DELETE SET NULL
    )

    worlds: Mapped[List["World"]] = relationship(
        "World",
        back_populates="owner", 
        cascade="all, delete-orphan" 
    )

    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Forum relationships
    forum_threads: Mapped[List["ForumThread"]] = relationship(
        "ForumThread",
        foreign_keys="[ForumThread.user_id]",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    forum_posts: Mapped[List["ForumPost"]] = relationship(
        "ForumPost",
        foreign_keys="[ForumPost.user_id]",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    forum_votes: Mapped[List["ForumVote"]] = relationship(
        "ForumVote",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    forum_subscriptions: Mapped[List["ForumSubscription"]] = relationship(
        "ForumSubscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Published stories relationships
    published_stories: Mapped[List["PublishedStory"]] = relationship(
        "PublishedStory",
        back_populates="publisher",
        cascade="all, delete-orphan"
    )
    
    story_comments: Mapped[List["StoryComment"]] = relationship(
        "StoryComment",
        back_populates="commenter",
        cascade="all, delete-orphan"
    )
    
    story_ratings: Mapped[List["StoryRating"]] = relationship(
        "StoryRating",
        back_populates="rater",
        cascade="all, delete-orphan"
    )
    
    # Billing relationship
    account: Mapped[Optional["UserAccount"]] = relationship(
        "UserAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    # Anonymous user sessions relationship
    anonymous_sessions: Mapped[List["AnonymousUserSession"]] = relationship(
        "AnonymousUserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # User activities relationship
    activities: Mapped[List["UserActivity"]] = relationship(
        "UserActivity",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Social sharing relationships
    social_shares: Mapped[List["SocialShare"]] = relationship(
        "SocialShare",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    social_share_summaries: Mapped[List["SocialShareDailySummary"]] = relationship(
        "SocialShareDailySummary",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Story chat sessions relationship - temporarily disabled until tables exist
    # story_chat_sessions: Mapped[List["StoryChatSession"]] = relationship(
    #     "StoryChatSession",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )
    
    # Interview responses relationship
    interview_responses: Mapped[List["UserInterviewResponse"]] = relationship(
        "UserInterviewResponse",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Brainstorm relationships
    brainstorm_sessions: Mapped[List["BrainstormSession"]] = relationship(
        "BrainstormSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    brainstorm_favorites: Mapped[List["BrainstormFavorite"]] = relationship(
        "BrainstormFavorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    brainstorm_stories: Mapped[List["BrainstormStory"]] = relationship(
        "BrainstormStory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Blog relationships
    blog_posts: Mapped[List["BlogPost"]] = relationship(
        "BlogPost",
        back_populates="author",
        cascade="all, delete-orphan"
    )
    
    blog_comments: Mapped[List["BlogComment"]] = relationship(
        "BlogComment",
        back_populates="author",
        cascade="all, delete-orphan"
    )
    
    blog_likes: Mapped[List["BlogLike"]] = relationship(
        "BlogLike",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    blog_views: Mapped[List["BlogView"]] = relationship(
        "BlogView",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Blog follow relationships (as author and as follower)
    blog_followers: Mapped[List["BlogFollow"]] = relationship(
        "BlogFollow",
        foreign_keys="[BlogFollow.author_id]",
        back_populates="author",
        cascade="all, delete-orphan"
    )
    
    blog_following: Mapped[List["BlogFollow"]] = relationship(
        "BlogFollow",
        foreign_keys="[BlogFollow.follower_id]",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    
    # Blog author profile
    blog_author_profile: Mapped[Optional["BlogAuthorProfile"]] = relationship(
        "BlogAuthorProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    # Blog subscriptions
    blog_subscriptions: Mapped[List["BlogSubscription"]] = relationship(
        "BlogSubscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    @property
    def is_oauth_user(self) -> bool:
        """Check if this is an OAuth user"""
        return self.auth_provider != 'local'
    
    @property
    def can_set_password(self) -> bool:
        """Check if user can set a password"""
        return True  # All users can set password
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', provider='{self.auth_provider}')>"