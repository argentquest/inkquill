import asyncio
import os 
import sys 
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config 

from alembic import context

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.db.database import Base
from app.core.config import SQLALCHEMY_DATABASE_URI

from app.models import *
# Explicitly import new chat models to ensure they're detected by alembic
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.chat_sample import ChatSample
# Explicitly import new billing models to ensure they're detected by alembic
from app.models.user_account import UserAccount
from app.models.user_transaction import UserTransaction
from app.models.credit_package import CreditPackage
# Explicitly import anonymous user session model
from app.models.anonymous_user_session import AnonymousUserSession
# Explicitly import new role-based association models
from app.models.world_role import WorldRole
from app.models.story_associations import StoryCharacterAssociation, StoryLocationAssociation, StoryLoreItemAssociation
from app.models.act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation
from app.models.scene_associations import SceneCharacterAssociation, SceneLocationAssociation, SceneLoreItemAssociation
# Explicitly import published story models
from app.models.published_story import PublishedStory
from app.models.story_comment import StoryComment
from app.models.story_rating import StoryRating
# Explicitly import brainstorm models
from app.models.brainstorm_session import BrainstormSession, BrainstormFavorite, BrainstormStory
# Explicitly import blog models to ensure they're detected by alembic
from app.models.blog_post import BlogPost
from app.models.blog_category import BlogCategory
from app.models.blog_tag import BlogTag
from app.models.blog_comment import BlogComment
from app.models.blog_like import BlogLike
from app.models.blog_follow import BlogFollow
from app.models.blog_view import BlogView
from app.models.blog_analytics_summary import BlogAnalyticsSummary
from app.models.blog_post_association import BlogPostAssociation
from app.models.blog_content_link import BlogContentLink
from app.models.blog_author_profile import BlogAuthorProfile
# Story chat models temporarily disabled
# from app.models.story_chat_session import StoryChatSession
# from app.models.story_chat_message import StoryChatMessage

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URI)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}, 
        compare_type=True 
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    print("Running migrations offline...")
    run_migrations_offline()
else:
    print("Running migrations online...")
    asyncio.run(run_migrations_online())