#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from app.models.published_story import PublishedStory
from app.models.story import Story
from app.models.act import Act
from app.models.scene import Scene
from dotenv import load_dotenv
import re

load_dotenv()

def extract_first_50_words(text: str) -> str:
    """Extract the first 50 words from text content."""
    if not text:
        return ""
    
    # Remove HTML tags and normalize whitespace
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Split into words and take first 50
    words = clean_text.split()
    if len(words) <= 50:
        return ' '.join(words)
    else:
        return ' '.join(words[:50])

async def get_story_first_words(db: AsyncSession, story_id: int) -> str:
    """Get the first 50 words from a story's content."""
    try:
        print(f"Checking story ID: {story_id}")
        
        # Get the first act's first scene content
        result = await db.execute(
            select(Scene.content)
            .join(Act)
            .where(Act.story_id == story_id)
            .where(Scene.content.isnot(None))
            .where(Scene.content != '')
            .order_by(Act.position.asc(), Scene.position.asc())
            .limit(1)
        )
        
        scene_content = result.scalar_one_or_none()
        print(f"Scene content found: {bool(scene_content)}")
        if scene_content:
            first_words = extract_first_50_words(scene_content)
            print(f"First words extracted: {first_words[:100]}...")
            return first_words
        
        # If no scene content, try act content
        result = await db.execute(
            select(Act.content)
            .where(Act.story_id == story_id)
            .where(Act.content.isnot(None))
            .where(Act.content != '')
            .order_by(Act.position.asc())
            .limit(1)
        )
        
        act_content = result.scalar_one_or_none()
        print(f"Act content found: {bool(act_content)}")
        if act_content:
            first_words = extract_first_50_words(act_content)
            print(f"First words from act: {first_words[:100]}...")
            return first_words
            
        print("No content found")
        return ""
    except Exception as e:
        print(f"Error getting first words for story {story_id}: {e}")
        return ""

async def test_story_preview():
    """Test the story preview functionality."""
    
    DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URI')
    if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    engine = create_async_engine(DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        # Get a few published stories
        result = await session.execute(
            select(PublishedStory)
            .where(PublishedStory.is_public == True)
            .limit(3)
        )
        stories = result.scalars().all()
        
        print(f"Found {len(stories)} published stories")
        
        for story in stories:
            print(f"\n--- Story: {story.title} (ID: {story.id}, Story ID: {story.story_id}) ---")
            if story.story_id:
                first_words = await get_story_first_words(session, story.story_id)
                print(f"First words result: '{first_words}'")
            else:
                print("No story_id associated")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_story_preview())