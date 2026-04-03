"""Add blog engine tables

Revision ID: abc123def456
Revises: f6f820dc421b
Create Date: 2025-07-15 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, None] = 'f6f820dc421b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create blog_categories table
    op.create_table('blog_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('post_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_blog_categories_id'), 'blog_categories', ['id'], unique=False)
    op.create_index(op.f('ix_blog_categories_slug'), 'blog_categories', ['slug'], unique=False)

    # Create blog_tags table
    op.create_table('blog_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_blog_tags_id'), 'blog_tags', ['id'], unique=False)
    op.create_index(op.f('ix_blog_tags_name'), 'blog_tags', ['name'], unique=False)
    op.create_index(op.f('ix_blog_tags_slug'), 'blog_tags', ['slug'], unique=False)

    # Create blog_posts table
    op.create_table('blog_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('featured_image_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'PUBLISHED', 'ARCHIVED', name='blogpoststatus'), nullable=False, server_default='DRAFT'),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comment_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('meta_title', sa.String(length=255), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('meta_keywords', sa.Text(), nullable=True),
        sa.Column('og_title', sa.String(length=255), nullable=True),
        sa.Column('og_description', sa.Text(), nullable=True),
        sa.Column('og_image_url', sa.String(length=500), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('allow_comments', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_ai_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['blog_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_blog_posts_id'), 'blog_posts', ['id'], unique=False)
    op.create_index(op.f('ix_blog_posts_title'), 'blog_posts', ['title'], unique=False)
    op.create_index(op.f('ix_blog_posts_slug'), 'blog_posts', ['slug'], unique=False)
    op.create_index(op.f('ix_blog_posts_status'), 'blog_posts', ['status'], unique=False)
    op.create_index(op.f('ix_blog_posts_author_id'), 'blog_posts', ['author_id'], unique=False)
    op.create_index(op.f('ix_blog_posts_category_id'), 'blog_posts', ['category_id'], unique=False)
    op.create_index(op.f('ix_blog_posts_published_at'), 'blog_posts', ['published_at'], unique=False)
    op.create_index('idx_blog_posts_author_status', 'blog_posts', ['author_id', 'status'], unique=False)
    op.create_index('idx_blog_posts_published_featured', 'blog_posts', ['published_at', 'is_featured'], unique=False)
    op.create_index('idx_blog_posts_category_status', 'blog_posts', ['category_id', 'status'], unique=False)
    op.create_index('idx_blog_posts_search_vector', 'blog_posts', ['search_vector'], unique=False, postgresql_using='gin')

    # Create blog_post_tags association table
    op.create_table('blog_post_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['blog_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create blog_comments table
    op.create_table('blog_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'DELETED', name='commentstatus'), nullable=False, server_default='APPROVED'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reply_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_author_reply', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['blog_comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_comments_id'), 'blog_comments', ['id'], unique=False)
    op.create_index(op.f('ix_blog_comments_post_id'), 'blog_comments', ['post_id'], unique=False)
    op.create_index(op.f('ix_blog_comments_author_id'), 'blog_comments', ['author_id'], unique=False)
    op.create_index(op.f('ix_blog_comments_parent_comment_id'), 'blog_comments', ['parent_comment_id'], unique=False)
    op.create_index(op.f('ix_blog_comments_status'), 'blog_comments', ['status'], unique=False)
    op.create_index(op.f('ix_blog_comments_created_at'), 'blog_comments', ['created_at'], unique=False)
    op.create_index('idx_blog_comments_post_status', 'blog_comments', ['post_id', 'status'], unique=False)
    op.create_index('idx_blog_comments_author_created', 'blog_comments', ['author_id', 'created_at'], unique=False)
    op.create_index('idx_blog_comments_parent_created', 'blog_comments', ['parent_comment_id', 'created_at'], unique=False)

    # Create blog_likes table
    op.create_table('blog_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'user_id', name='unique_post_like')
    )
    op.create_index(op.f('ix_blog_likes_id'), 'blog_likes', ['id'], unique=False)
    op.create_index(op.f('ix_blog_likes_post_id'), 'blog_likes', ['post_id'], unique=False)
    op.create_index(op.f('ix_blog_likes_user_id'), 'blog_likes', ['user_id'], unique=False)

    # Create blog_follows table
    op.create_table('blog_follows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('notification_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('author_id', 'follower_id', name='unique_author_follower')
    )
    op.create_index(op.f('ix_blog_follows_id'), 'blog_follows', ['id'], unique=False)
    op.create_index(op.f('ix_blog_follows_author_id'), 'blog_follows', ['author_id'], unique=False)
    op.create_index(op.f('ix_blog_follows_follower_id'), 'blog_follows', ['follower_id'], unique=False)

    # Create blog_views table
    op.create_table('blog_views',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('referrer_url', sa.String(length=500), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('view_duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_views_id'), 'blog_views', ['id'], unique=False)
    op.create_index(op.f('ix_blog_views_post_id'), 'blog_views', ['post_id'], unique=False)
    op.create_index(op.f('ix_blog_views_user_id'), 'blog_views', ['user_id'], unique=False)
    op.create_index(op.f('ix_blog_views_ip_address'), 'blog_views', ['ip_address'], unique=False)
    op.create_index(op.f('ix_blog_views_created_at'), 'blog_views', ['created_at'], unique=False)

    # Create blog_analytics_summary table
    op.create_table('blog_analytics_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('unique_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('new_likes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('new_comments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_read_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bounce_rate', sa.DECIMAL(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('social_shares', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'date', name='unique_post_date')
    )
    op.create_index(op.f('ix_blog_analytics_summary_id'), 'blog_analytics_summary', ['id'], unique=False)
    op.create_index(op.f('ix_blog_analytics_summary_post_id'), 'blog_analytics_summary', ['post_id'], unique=False)
    op.create_index(op.f('ix_blog_analytics_summary_date'), 'blog_analytics_summary', ['date'], unique=False)

    # Create blog_post_associations table
    op.create_table('blog_post_associations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('association_type', sa.Enum('STORY', 'WORLD', 'CHARACTER', 'LOCATION', 'LORE_ITEM', name='associationtype'), nullable=False),
        sa.Column('association_id', sa.Integer(), nullable=False),
        sa.Column('association_title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_post_associations_id'), 'blog_post_associations', ['id'], unique=False)
    op.create_index(op.f('ix_blog_post_associations_post_id'), 'blog_post_associations', ['post_id'], unique=False)
    op.create_index(op.f('ix_blog_post_associations_association_type'), 'blog_post_associations', ['association_type'], unique=False)
    op.create_index(op.f('ix_blog_post_associations_association_id'), 'blog_post_associations', ['association_id'], unique=False)
    op.create_index(op.f('ix_blog_post_associations_created_at'), 'blog_post_associations', ['created_at'], unique=False)

    # Create blog_content_links table
    op.create_table('blog_content_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('link_type', sa.Enum('CHARACTER', 'LOCATION', 'LORE_ITEM', name='linktype'), nullable=False),
        sa.Column('link_id', sa.Integer(), nullable=False),
        sa.Column('link_text', sa.String(length=255), nullable=True),
        sa.Column('link_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_content_links_id'), 'blog_content_links', ['id'], unique=False)
    op.create_index(op.f('ix_blog_content_links_post_id'), 'blog_content_links', ['post_id'], unique=False)
    op.create_index(op.f('ix_blog_content_links_link_type'), 'blog_content_links', ['link_type'], unique=False)
    op.create_index(op.f('ix_blog_content_links_link_id'), 'blog_content_links', ['link_id'], unique=False)

    # Create blog_author_profiles table
    op.create_table('blog_author_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True),
        sa.Column('website_url', sa.String(length=255), nullable=True),
        sa.Column('twitter_handle', sa.String(length=50), nullable=True),
        sa.Column('instagram_handle', sa.String(length=50), nullable=True),
        sa.Column('linkedin_url', sa.String(length=255), nullable=True),
        sa.Column('allow_comments_default', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('auto_publish', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('total_posts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_likes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('follower_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='unique_user_profile')
    )
    op.create_index(op.f('ix_blog_author_profiles_id'), 'blog_author_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_blog_author_profiles_user_id'), 'blog_author_profiles', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('blog_author_profiles')
    op.drop_table('blog_content_links')
    op.drop_table('blog_post_associations')
    op.drop_table('blog_analytics_summary')
    op.drop_table('blog_views')
    op.drop_table('blog_follows')
    op.drop_table('blog_likes')
    op.drop_table('blog_comments')
    op.drop_table('blog_post_tags')
    op.drop_table('blog_posts')
    op.drop_table('blog_tags')
    op.drop_table('blog_categories')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS blogpoststatus')
    op.execute('DROP TYPE IF EXISTS commentstatus')
    op.execute('DROP TYPE IF EXISTS associationtype')
    op.execute('DROP TYPE IF EXISTS linktype')