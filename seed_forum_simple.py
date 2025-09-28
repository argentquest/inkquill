#!/usr/bin/env python3
"""Simple script to seed forum data using SQLAlchemy."""

import os
import sys
import asyncio
import asyncpg

# Database connection parameters
DB_CONFIG = {
    'user': 'sw2app',
    'password': 'Allen2156!',
    'host': 'sw2db.postgres.database.azure.com',
    'port': 5432,
    'database': 'devstory2'
}

async def seed_forum_data():
    """Seed forum data."""
    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        print("Connected to database successfully")
        
        # Check if categories exist
        categories_count = await conn.fetchval("SELECT COUNT(*) FROM forum_categories")
        print(f"Current forum categories: {categories_count}")
        
        if categories_count == 0:
            print("Inserting forum categories...")
            await conn.execute("""
                INSERT INTO forum_categories (name, description, slug, sort_order, is_active, icon, created_at, updated_at)
                VALUES 
                    ('General Discussion', 'General chat and discussion topics', 'general-discussion', 1, true, 'chat', NOW(), NOW()),
                    ('World Building', 'Discuss world building techniques and share worlds', 'world-building', 2, true, 'world', NOW(), NOW()),
                    ('Story Writing', 'Share stories, get feedback, and discuss writing', 'story-writing', 3, true, 'book', NOW(), NOW()),
                    ('Feature Requests', 'Suggest new features and improvements', 'feature-requests', 4, true, 'lightbulb', NOW(), NOW()),
                    ('Technical Support', 'Get help with technical issues', 'technical-support', 5, true, 'help', NOW(), NOW())
            """)
            print("Categories inserted")
        
        # Check if admin user exists
        admin_user = await conn.fetchrow("SELECT id FROM users WHERE username = 'admin' LIMIT 1")
        if not admin_user:
            print("No admin user found. Creating forum data will be skipped.")
            await conn.close()
            return
        
        admin_id = admin_user['id']
        print(f"Found admin user with ID: {admin_id}")
        
        # Check if threads exist
        threads_count = await conn.fetchval("SELECT COUNT(*) FROM forum_threads")
        print(f"Current forum threads: {threads_count}")
        
        if threads_count == 0:
            print("Inserting forum threads...")
            
            # Get category IDs
            general_cat = await conn.fetchval("SELECT id FROM forum_categories WHERE slug = 'general-discussion'")
            worldbuilding_cat = await conn.fetchval("SELECT id FROM forum_categories WHERE slug = 'world-building'")
            writing_cat = await conn.fetchval("SELECT id FROM forum_categories WHERE slug = 'story-writing'")
            
            # Insert threads
            await conn.execute("""
                INSERT INTO forum_threads (title, slug, status, category_id, user_id, view_count, post_count, is_pinned, is_locked, is_deleted, created_at, updated_at)
                VALUES 
                    ($1, $2, $3, $4, $5, 0, 0, true, false, false, NOW(), NOW()),
                    ($6, $7, $8, $9, $10, 0, 0, false, false, false, NOW(), NOW()),
                    ($11, $12, $13, $14, $15, 0, 0, false, false, false, NOW(), NOW())
            """, 
                'Welcome to the Community!', 'welcome-to-the-community', 'OPEN', general_cat, admin_id,
                'Tips for Creating Compelling Characters', 'tips-for-creating-compelling-characters', 'OPEN', worldbuilding_cat, admin_id,
                'Share Your Latest Story', 'share-your-latest-story', 'OPEN', writing_cat, admin_id
            )
            print("Threads inserted")
        
        # Check if posts exist
        posts_count = await conn.fetchval("SELECT COUNT(*) FROM forum_posts")
        print(f"Current forum posts: {posts_count}")
        
        if posts_count == 0:
            print("Inserting forum posts...")
            
            # Get thread IDs
            welcome_thread = await conn.fetchval("SELECT id FROM forum_threads WHERE slug = 'welcome-to-the-community'")
            characters_thread = await conn.fetchval("SELECT id FROM forum_threads WHERE slug = 'tips-for-creating-compelling-characters'")
            stories_thread = await conn.fetchval("SELECT id FROM forum_threads WHERE slug = 'share-your-latest-story'")
            
            # Insert posts
            await conn.execute("""
                INSERT INTO forum_posts (content, thread_id, user_id, is_deleted, created_at, updated_at)
                VALUES 
                    ($1, $2, $3, false, NOW(), NOW()),
                    ($4, $5, $6, false, NOW(), NOW()),
                    ($7, $8, $9, false, NOW(), NOW())
            """,
                'Welcome to our AI Storytelling Community! This is a place where writers, world-builders, and creative minds come together to share ideas, get feedback, and explore the possibilities of AI-assisted storytelling. Feel free to introduce yourself and let us know what brings you here!',
                welcome_thread, admin_id,
                
                'Creating compelling characters is one of the most important aspects of storytelling. Here are some tips I have learned over the years: 1. Give your characters clear motivations and goals, 2. Create internal conflicts that drive their actions, 3. Develop unique voices and speech patterns, 4. Build backstories that inform their present behavior. What techniques do you use to develop your characters?',
                characters_thread, admin_id,
                
                'I would love to see what stories everyone is working on! Whether it is a short piece, a novel, or just an idea you are developing, share it here. We are all here to support each other and provide constructive feedback. I will start: I am currently working on a science fiction story about a colony ship that discovers something unexpected in deep space. Still figuring out the details, but I am excited about the concept!',
                stories_thread, admin_id
            )
            print("Posts inserted")
            
            # Update thread metadata
            await conn.execute("""
                UPDATE forum_threads SET 
                    post_count = (
                        SELECT COUNT(*) 
                        FROM forum_posts 
                        WHERE thread_id = forum_threads.id AND is_deleted = false
                    ),
                    last_post_at = (
                        SELECT MAX(created_at) 
                        FROM forum_posts 
                        WHERE thread_id = forum_threads.id AND is_deleted = false
                    ),
                    last_post_by_id = (
                        SELECT fp.user_id 
                        FROM forum_posts fp 
                        WHERE fp.thread_id = forum_threads.id AND fp.is_deleted = false
                        ORDER BY fp.created_at DESC 
                        LIMIT 1
                    )
                WHERE EXISTS (
                    SELECT 1 FROM forum_posts 
                    WHERE thread_id = forum_threads.id AND is_deleted = false
                )
            """)
            print("Thread metadata updated")
        
        # Show final counts
        categories_final = await conn.fetchval("SELECT COUNT(*) FROM forum_categories")
        threads_final = await conn.fetchval("SELECT COUNT(*) FROM forum_threads")
        posts_final = await conn.fetchval("SELECT COUNT(*) FROM forum_posts")
        
        print(f"\nFinal counts:")
        print(f"Categories: {categories_final}")
        print(f"Threads: {threads_final}")
        print(f"Posts: {posts_final}")
        
        await conn.close()
        print("Forum seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding forum data: {e}")

if __name__ == "__main__":
    asyncio.run(seed_forum_data())