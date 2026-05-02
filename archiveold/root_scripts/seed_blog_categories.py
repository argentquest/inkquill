import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from app.db.database import async_session_local
from app.models.blog_category import BlogCategory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_blog_categories():
    """Seed initial blog categories for the blogging engine"""
    
    categories = [
        {
            "name": "Writing Tips",
            "slug": "writing-tips",
            "description": "Tips and techniques for better storytelling and writing",
            "color": "#3b82f6",  # Blue
            "icon": "📝",
            "display_order": 1
        },
        {
            "name": "World Building",
            "slug": "world-building", 
            "description": "Creating immersive worlds and settings for your stories",
            "color": "#10b981",  # Green
            "icon": "🌍",
            "display_order": 2
        },
        {
            "name": "Character Development",
            "slug": "character-development",
            "description": "Crafting compelling characters and their journeys",
            "color": "#f59e0b",  # Yellow
            "icon": "👥",
            "display_order": 3
        },
        {
            "name": "Plot & Structure",
            "slug": "plot-structure",
            "description": "Story structure, pacing, and plot development techniques",
            "color": "#ef4444",  # Red
            "icon": "📊",
            "display_order": 4
        },
        {
            "name": "AI Writing",
            "slug": "ai-writing",
            "description": "Using AI tools and techniques to enhance your writing",
            "color": "#8b5cf6",  # Purple
            "icon": "🤖",
            "display_order": 5
        },
        {
            "name": "Publishing",
            "slug": "publishing",
            "description": "Getting your stories published and reaching readers",
            "color": "#06b6d4",  # Cyan
            "icon": "📚",
            "display_order": 6
        },
        {
            "name": "Community",
            "slug": "community",
            "description": "Community discussions, events, and writer spotlights",
            "color": "#ec4899",  # Pink
            "icon": "🤝",
            "display_order": 7
        },
        {
            "name": "Behind the Scenes",
            "slug": "behind-the-scenes",
            "description": "Author insights into their creative process and journey",
            "color": "#64748b",  # Gray
            "icon": "🎬",
            "display_order": 8
        }
    ]
    
    async with async_session_local() as db:
        try:
            # Check if categories already exist
            existing_categories = await db.execute(
                select(func.count()).select_from(BlogCategory)
            )
            count = existing_categories.scalar()
            
            if count > 0:
                logger.info(f"Found {count} existing blog categories. Skipping seed.")
                return
            
            # Create categories
            for category_data in categories:
                category = BlogCategory(**category_data)
                db.add(category)
            
            await db.commit()
            logger.info(f"Successfully seeded {len(categories)} blog categories!")
            
        except Exception as e:
            logger.error(f"Error seeding blog categories: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_blog_categories())