#!/usr/bin/env python3
"""Seed app-scoped forum categories for Circle Friends and Storytelling.

Run from repo root:
    python scripts/seed_forum_categories.py
"""
import asyncio
import sys

sys.path.insert(0, ".")

from sqlalchemy import select
from app.db.database import async_session_local
from app.models.forum import ForumCategory


CARE_CIRCLE_CATEGORIES = [
    {"name": "Care Tips & Resources", "slug": "care-tips-resources", "description": "Caregiving advice, medical info, daily routines, and best practices", "sort_order": 1, "icon": "🩺"},
    {"name": "Family Coordination", "slug": "family-coordination", "description": "Planning, schedules, events, and logistics for the care circle", "sort_order": 2, "icon": "📅"},
    {"name": "Memory Lane", "slug": "memory-lane", "description": "Sharing memories, photos, and stories about friends and loved ones", "sort_order": 3, "icon": "📸"},
    {"name": "Wellness & Activities", "slug": "wellness-activities", "description": "Ideas for outings, activities, and keeping friends engaged", "sort_order": 4, "icon": "🌿"},
    {"name": "Getting Help", "slug": "getting-help", "description": "Questions about using the Circle Friends app and troubleshooting", "sort_order": 5, "icon": "❓"},
]

STORYTELLING_CATEGORIES = [
    {"name": "Story Feedback & Critique", "slug": "story-feedback-critique", "description": "Share works-in-progress and get reader feedback", "sort_order": 1, "icon": "💬"},
    {"name": "World Building", "slug": "world-building", "description": "Discuss worlds, lore, settings, and fictional history", "sort_order": 2, "icon": "🌍"},
    {"name": "Character Workshop", "slug": "character-workshop", "description": "Character development, backstories, and motivation deep-dives", "sort_order": 3, "icon": "🎭"},
    {"name": "Writing Craft & Tips", "slug": "writing-craft-tips", "description": "General writing advice, prompts, and technique discussions", "sort_order": 4, "icon": "📝"},
    {"name": "AI Collaboration", "slug": "ai-collaboration", "description": "Strategies for working with AI tools, prompt tips, and generation techniques", "sort_order": 5, "icon": "🤖"},
]


async def seed_categories() -> None:
    async with async_session_local() as db:
        for source, categories in [
            ("care-circle", CARE_CIRCLE_CATEGORIES),
            ("storytelling", STORYTELLING_CATEGORIES),
        ]:
            for data in categories:
                result = await db.execute(
                    select(ForumCategory).where(
                        ForumCategory.app_source == source,
                        ForumCategory.slug == data["slug"],
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    print(f"Skipping existing category: {existing.name} ({source})")
                    continue

                category = ForumCategory(
                    name=data["name"],
                    slug=data["slug"],
                    description=data["description"],
                    sort_order=data["sort_order"],
                    icon=data["icon"],
                    app_source=source,
                    is_active=True,
                )
                db.add(category)
                print(f"Added category: {data['name']} ({source})")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed_categories())
