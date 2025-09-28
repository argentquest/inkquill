#!/usr/bin/env python3
"""
Script to check existing QUICK_AI prompts in the database
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.db.database import AsyncSessionLocal
from app.models.prompt import Prompt, PromptTypeEnum
from sqlalchemy import select

async def check_quick_ai_prompts():
    """Check existing QUICK_AI prompts in database"""
    async with AsyncSessionLocal() as session:
        # Query for QUICK_AI prompts
        result = await session.execute(
            select(Prompt).where(Prompt.prompt_type == PromptTypeEnum.QUICK_AI)
        )
        quick_ai_prompts = result.scalars().all()
        
        print(f"Found {len(quick_ai_prompts)} QUICK_AI prompts in database:")
        print("-" * 50)
        
        for prompt in quick_ai_prompts:
            print(f"ID: {prompt.id}")
            print(f"Title: {prompt.title}")
            print(f"Active: {prompt.is_active}")
            print(f"Created: {prompt.created_at}")
            print(f"Content: {prompt.prompt_content[:100]}...")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(check_quick_ai_prompts())