#!/usr/bin/env python3
"""Script to seed forum categories, threads, and posts for testing."""

import sys
import os
sys.path.insert(0, '.')

import asyncio
from sqlalchemy import select

# Manually set required environment variables
os.environ['POSTGRES_USER'] = 'sw2app'
os.environ['POSTGRES_PASSWORD'] = 'Allen2156!'
os.environ['POSTGRES_SERVER'] = 'sw2db.postgres.database.azure.com'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DB'] = 'devstory2'

from app.db.database import async_session_maker
from app.models.forum import ForumCategory, ForumThread, ForumPost
from app.models.user import User

async def seed_forum_data():
    """Seed forum data for testing."""
    async with async_session_maker() as db:
        # Check if categories already exist
        result = await db.execute(select(ForumCategory).limit(1))
        if result.scalar_one_or_none():
            print("Forum categories already exist. Skipping seeding.")
            return
        
        # Create categories
        print("Creating forum categories...")
        categories = [
            ForumCategory(
                name="General Discussion",
                description="General chat and discussion topics",
                slug="general-discussion",
                sort_order=1,
                is_active=True,
                icon="chat"
            ),
            ForumCategory(
                name="World Building",
                description="Discuss world building techniques and share worlds",
                slug="world-building",
                sort_order=2,
                is_active=True,
                icon="world"
            ),
            ForumCategory(
                name="Story Writing",
                description="Share stories, get feedback, and discuss writing",
                slug="story-writing",
                sort_order=3,
                is_active=True,
                icon="book"
            ),
            ForumCategory(
                name="Feature Requests",
                description="Suggest new features and improvements",
                slug="feature-requests",
                sort_order=4,
                is_active=True,
                icon="lightbulb"
            ),
            ForumCategory(
                name="Technical Support",
                description="Get help with technical issues",
                slug="technical-support",
                sort_order=5,
                is_active=True,
                icon="help"
            )
        ]
        
        for category in categories:
            db.add(category)
        
        await db.commit()
        print(f"Created {len(categories)} forum categories")
        
        # Get a test user (assume admin exists)
        result = await db.execute(select(User).where(User.username == "admin"))
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            print("Admin user not found. Creating test user...")
            # You might need to create a test user here
            return
        
        # Create some threads
        print("Creating forum threads...")
        threads = [
            ForumThread(
                title="Welcome to the Community!",
                slug="welcome-to-the-community",
                category_id=categories[0].id,
                user_id=admin_user.id,
                view_count=0,
                post_count=1,
                is_pinned=True,
                is_locked=False,
                is_deleted=False
            ),
            ForumThread(
                title="Tips for Creating Compelling Characters",
                slug="tips-for-creating-compelling-characters",
                category_id=categories[1].id,
                user_id=admin_user.id,
                view_count=0,
                post_count=1,
                is_pinned=False,
                is_locked=False,
                is_deleted=False
            ),
            ForumThread(
                title="Share Your Latest Story",
                slug="share-your-latest-story",
                category_id=categories[2].id,
                user_id=admin_user.id,
                view_count=0,
                post_count=1,
                is_pinned=False,
                is_locked=False,
                is_deleted=False
            )
        ]
        
        for thread in threads:
            db.add(thread)
        
        await db.commit()
        print(f"Created {len(threads)} forum threads")
        
        # Create some posts
        print("Creating forum posts...")
        posts = [
            ForumPost(
                content="Welcome to our AI Storytelling Community! This is a place where writers, world-builders, and creative minds come together to share ideas, get feedback, and explore the possibilities of AI-assisted storytelling. Feel free to introduce yourself and let us know what brings you here!",
                thread_id=threads[0].id,
                user_id=admin_user.id,
                is_deleted=False
            ),
            ForumPost(
                content="Creating compelling characters is one of the most important aspects of storytelling. Here are some tips I've learned over the years:\\n\\n1. Give your characters clear motivations and goals\\n2. Create internal conflicts that drive their actions\\n3. Develop unique voices and speech patterns\\n4. Build backstories that inform their present behavior\\n\\nWhat techniques do you use to develop your characters?",
                thread_id=threads[1].id,
                user_id=admin_user.id,
                is_deleted=False
            ),
            ForumPost(
                content="I'd love to see what stories everyone is working on! Whether it's a short piece, a novel, or just an idea you're developing, share it here. We're all here to support each other and provide constructive feedback.\\n\\nI'll start: I'm currently working on a science fiction story about a colony ship that discovers something unexpected in deep space. Still figuring out the details, but I'm excited about the concept!",
                thread_id=threads[2].id,
                user_id=admin_user.id,
                is_deleted=False
            )
        ]
        
        for post in posts:
            db.add(post)
        
        await db.commit()
        print(f"Created {len(posts)} forum posts")
        
        # Update thread post counts and last post info
        for i, thread in enumerate(threads):
            thread.post_count = 1
            thread.last_post_at = posts[i].created_at
            thread.last_post_by_id = admin_user.id
        
        await db.commit()
        print("Updated thread metadata")
        
        print("\\nForum seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_forum_data())