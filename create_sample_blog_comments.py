#!/usr/bin/env python3
"""Create sample blog data for testing comments functionality."""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import engine
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_comment import BlogComment, CommentStatus
from app.models.user import User

async def create_sample_data():
    """Create sample blog posts and comments."""
    async with AsyncSession(engine) as session:
        
        # Get first user
        result = await session.execute(select(User).where(User.is_active == True))
        user = result.scalar_one_or_none()
        
        if not user:
            print("No active users found. Please create a user first.")
            return
        
        print(f"Using user: {user.username} (ID: {user.id})")
        
        # Create sample blog post if none exist
        result = await session.execute(
            select(BlogPost).where(BlogPost.status == BlogPostStatus.PUBLISHED)
        )
        existing_posts = result.scalars().all()
        
        if not existing_posts:
            print("Creating sample blog post...")
            blog_post = BlogPost(
                title="Welcome to Our Blog",
                slug="welcome-to-our-blog",
                content="""
                <h2>Welcome to Our Blog!</h2>
                <p>This is a sample blog post to test the commenting functionality. We're excited to share our thoughts and hear from you in the comments below.</p>
                <p>Feel free to leave a comment and start a discussion!</p>
                """,
                excerpt="Welcome to our blog! This is a sample post to test commenting.",
                author_id=user.id,
                status=BlogPostStatus.PUBLISHED,
                published_at=datetime.utcnow(),
                allow_comments=True,
                view_count=42,
                like_count=5,
                comment_count=0
            )
            session.add(blog_post)
            await session.flush()
            print(f"Created blog post: {blog_post.title} (ID: {blog_post.id})")
        else:
            blog_post = existing_posts[0]
            # Ensure comments are allowed
            blog_post.allow_comments = True
            print(f"Using existing blog post: {blog_post.title} (ID: {blog_post.id})")
        
        # Create sample comments
        print("Creating sample comments...")
        
        # Top-level comment 1
        comment1 = BlogComment(
            post_id=blog_post.id,
            author_id=user.id,
            content="Great post! I really enjoyed reading this. Looking forward to more content like this.",
            status=CommentStatus.APPROVED,
            like_count=3,
            reply_count=1,
            is_author_reply=False
        )
        session.add(comment1)
        await session.flush()
        
        # Reply to comment 1
        reply1 = BlogComment(
            post_id=blog_post.id,
            author_id=user.id,
            parent_comment_id=comment1.id,
            content="Thank you for the kind words! We're glad you enjoyed it.",
            status=CommentStatus.APPROVED,
            like_count=1,
            reply_count=0,
            is_author_reply=True
        )
        session.add(reply1)
        
        # Top-level comment 2
        comment2 = BlogComment(
            post_id=blog_post.id,
            author_id=user.id,
            content="This is exactly what I was looking for. The explanation is clear and easy to follow.",
            status=CommentStatus.APPROVED,
            like_count=2,
            reply_count=0,
            is_author_reply=False
        )
        session.add(comment2)
        
        # Top-level comment 3
        comment3 = BlogComment(
            post_id=blog_post.id,
            author_id=user.id,
            content="Interesting perspective! I'd love to see more posts on this topic.",
            status=CommentStatus.APPROVED,
            like_count=1,
            reply_count=0,
            is_author_reply=False
        )
        session.add(comment3)
        
        # Update post comment count
        blog_post.comment_count = 4
        
        await session.commit()
        
        print(f"Created 4 sample comments for post '{blog_post.title}'")
        print(f"Post URL: /blog/posts/{blog_post.slug}")
        print("Sample data creation completed!")

if __name__ == "__main__":
    asyncio.run(create_sample_data())