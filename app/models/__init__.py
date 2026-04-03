"""Package exports for models."""

# /story_app/app/models/__init__.py

# Import in a logical order, starting with independent models or enums
# and ending with models that have foreign keys to others.

from .user import User
from .refresh_token import RefreshToken
from .prompt import Prompt, PromptTypeEnum, AgeTargetEnum
from .ai_model_config import AIModelConfiguration, AIProviderEnum, AIModelTypeEnum
from .job_status import JobStatus
from .world_role import WorldRole
from .world_collaborator import WorldCollaborator, CollaboratorRole, CollaboratorStatus
from .world import World
from .story_class import StoryClass
from .story import Story
from .act import Act
from .scene import Scene
from .generated_image import GeneratedImage
from .location import Location, story_location_association_table, LocationConnection
from .character import Character, story_character_association_table
from .lore_item import LoreItem, story_lore_item_association_table

# Chat models
from .chat_session import ChatSession
from .chat_message import ChatMessage
from .chat_sample import ChatSample

# Anonymous user session tracking
from .anonymous_user_session import AnonymousUserSession

# User activity logging
from .user_activity import UserActivity

# Social sharing models
from .social_share import SocialShare, SocialShareDailySummary

# Forum models
from .forum import ForumCategory, ForumThread, ForumPost, ForumVote, ForumSubscription, ThreadStatus, VoteType

# Billing models
from .user_account import UserAccount
from .user_transaction import UserTransaction, TransactionType
from .credit_package import CreditPackage

# World hierarchy and role-based association models
from .story_associations import StoryCharacterAssociation, StoryLocationAssociation, StoryLoreItemAssociation
from .act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation
from .scene_associations import SceneCharacterAssociation, SceneLocationAssociation, SceneLoreItemAssociation

# Interview responses
from .user_interview_response import UserInterviewResponse

# Brainstorm session models
from .brainstorm_session import BrainstormSession, BrainstormFavorite, BrainstormStory

# This model has the most foreign keys, so we place it last.
from .uploaded_document import UploadedDocument
from .ai_cost_log import AICallLog

# Published story models
from .published_story import PublishedStory
from .story_comment import StoryComment
from .story_rating import StoryRating

# Blog models
from .blog_category import BlogCategory
from .blog_tag import BlogTag, blog_post_tags
from .blog_post import BlogPost, BlogPostStatus
from .blog_comment import BlogComment, CommentStatus
from .blog_like import BlogLike
from .blog_follow import BlogFollow
from .blog_view import BlogView
from .blog_analytics_summary import BlogAnalyticsSummary
from .blog_post_association import BlogPostAssociation, AssociationType
from .blog_content_link import BlogContentLink, LinkType
from .blog_author_profile import BlogAuthorProfile
from .blog_subscription import BlogSubscription


from .story_chat_session import StoryChatSession
from .story_chat_message import StoryChatMessage

# CTA Content models
from .cta_content import CTAContent, CTAPosition, CTAStyle

# By importing all models here, we ensure that SQLAlchemy's declarative base
# has a complete picture of all tables and their relationships before the
# application starts trying to use them, preventing NameError issues with
# forward-referenced relationship strings.

