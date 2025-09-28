#!/usr/bin/env python3
"""Test script to check blog posts and comments in database."""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import engine
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_comment import BlogComment, CommentStatus
from app.models.user import User

async def test_blog_data():
    """Test blog posts and comments."""
    async with AsyncSession(engine) as session:
        
        # Check blog posts
        print("=== BLOG POSTS ===")
        result = await session.execute(
            select(BlogPost)
            .where(BlogPost.status == BlogPostStatus.PUBLISHED)
        )
        posts = result.scalars().all()
        
        if not posts:
            print("No published blog posts found")
            return
        
        for post in posts:
            print(f"Post {post.id}: {post.title} (Comments allowed: {post.allow_comments})")
        
        # Check comments for first post
        first_post = posts[0]
        print(f"\n=== COMMENTS FOR POST {first_post.id} ===")
        
        result = await session.execute(
            select(BlogComment)
            .where(BlogComment.post_id == first_post.id)
        )
        comments = result.scalars().all()
        
        if not comments:
            print("No comments found")
        else:
            for comment in comments:
                print(f"Comment {comment.id}: '{comment.content}' (Status: {comment.status})")
        
        # Check users
        print(f"\n=== USERS ===")
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users[:5]:  # Show first 5 users
            print(f"User {user.id}: {user.username} (Active: {user.is_active})")

if __name__ == "__main__":
    asyncio.run(test_blog_data())