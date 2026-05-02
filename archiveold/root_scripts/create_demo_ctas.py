#!/usr/bin/env python3
"""
Script to create 11 demo CTA records to showcase all home page positions.
Run with: python create_demo_ctas.py
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_async_session
from app.models.cta_content import CTAContent, CTAPosition, CTAStyle

async def create_demo_ctas():
    """Create 11 demo CTAs for all home page positions."""
    
    cta_demos = [
        {
            "position": CTAPosition.HOME_MAIN_TOP,
            "title": "🎯 Main Top CTA",
            "subtitle": "This appears at the very top of main content",
            "content": "<p>Perfect for important announcements or primary call-to-actions.</p>",
            "style": CTAStyle.HERO,
            "background_color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "primary_button_text": "Get Started",
            "primary_button_url": "/ui/register",
            "primary_button_icon": "fas fa-rocket"
        },
        {
            "position": CTAPosition.HOME_WELCOME_TOP,
            "title": "👋 Welcome Section Top",
            "subtitle": "Appears above the welcome header section",
            "content": "<p>Great for onboarding messages or special offers for new users.</p>",
            "style": CTAStyle.GRADIENT,
            "background_color": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
            "primary_button_text": "Start Tutorial",
            "primary_button_url": "/ui/user-guide",
            "primary_button_icon": "fas fa-play-circle"
        },
        {
            "position": CTAPosition.HOME_WELCOME_BOTTOM,
            "title": "✨ Welcome Section Bottom",
            "subtitle": "Shows after the progress steps",
            "content": "<p>Ideal for encouraging users to complete onboarding steps.</p>",
            "style": CTAStyle.SOLID,
            "background_color": "#4c6ef5",
            "primary_button_text": "Complete Setup",
            "primary_button_url": "/ui/brainstorm",
            "primary_button_icon": "fas fa-check-circle"
        },
        {
            "position": CTAPosition.HOME_QUICK_ACTIONS_TOP,
            "title": "⚡ Quick Actions Top",
            "subtitle": "Before the quick actions buttons",
            "content": "<p>Perfect for highlighting featured actions or tools.</p>",
            "style": CTAStyle.BORDERED,
            "background_color": "#ffffff",
            "text_color": "#495057",
            "primary_button_text": "Featured Tool",
            "primary_button_url": "/ui/brainstorm",
            "primary_button_icon": "fas fa-star"
        },
        {
            "position": CTAPosition.HOME_QUICK_ACTIONS_BOTTOM,
            "title": "🚀 Quick Actions Bottom",
            "subtitle": "After all the quick action buttons",
            "content": "<p>Great for promoting advanced features or premium content.</p>",
            "style": CTAStyle.GRADIENT,
            "background_color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "primary_button_text": "Explore More",
            "primary_button_url": "/ui/stories",
            "primary_button_icon": "fas fa-arrow-right"
        },
        {
            "position": CTAPosition.HOME_LOGIN_REGISTER_TOP,
            "title": "🔐 Login/Register Top",
            "subtitle": "Above login/register section (anonymous users only)",
            "content": "<p>Shows special offers or incentives for registration.</p>",
            "style": CTAStyle.HERO,
            "background_color": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
            "primary_button_text": "Join Now",
            "primary_button_url": "/ui/register",
            "primary_button_icon": "fas fa-user-plus",
            "show_for_anonymous": True,
            "show_for_authenticated": False
        },
        {
            "position": CTAPosition.HOME_LOGIN_REGISTER_BOTTOM,
            "title": "💎 Login/Register Bottom",
            "subtitle": "Below login/register section (anonymous users only)",
            "content": "<p>Perfect for highlighting benefits of membership.</p>",
            "style": CTAStyle.SOLID,
            "background_color": "#28a745",
            "primary_button_text": "See Benefits",
            "primary_button_url": "/ui/register",
            "primary_button_icon": "fas fa-crown",
            "show_for_anonymous": True,
            "show_for_authenticated": False
        },
        {
            "position": CTAPosition.HOME_BLOG_SECTION_TOP,
            "title": "📝 Blog Section Top",
            "subtitle": "Above the latest blog posts section",
            "content": "<p>Great for promoting blog engagement or writing tools.</p>",
            "style": CTAStyle.MINIMAL,
            "background_color": "#f8f9fa",
            "text_color": "#495057",
            "primary_button_text": "Start Writing",
            "primary_button_url": "/blog/editor",
            "primary_button_icon": "fas fa-pen-nib"
        },
        {
            "position": CTAPosition.HOME_BLOG_SECTION_BOTTOM,
            "title": "📚 Blog Section Bottom", 
            "subtitle": "Below the latest blog posts section",
            "content": "<p>Encourage users to read more blog posts or write their own.</p>",
            "style": CTAStyle.GRADIENT,
            "background_color": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
            "primary_button_text": "Read More",
            "primary_button_url": "/blog",
            "primary_button_icon": "fas fa-book-open"
        },
        {
            "position": CTAPosition.HOME_MAIN_BOTTOM,
            "title": "🎯 Main Bottom CTA",
            "subtitle": "Final CTA at bottom of main content",
            "content": "<p>Last chance to convert users before they reach the sidebar.</p>",
            "style": CTAStyle.HERO,
            "background_color": "linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)",
            "primary_button_text": "Take Action",
            "primary_button_url": "/ui/register",
            "primary_button_icon": "fas fa-bolt"
        },
        {
            "position": CTAPosition.HOME_SIDEBAR_TOP,
            "title": "📌 Sidebar Top",
            "subtitle": "Top of right sidebar column",
            "content": "<p>Excellent for sticky promotions or important notices.</p>",
            "style": CTAStyle.SOLID,
            "background_color": "#6c757d",
            "primary_button_text": "Learn More",
            "primary_button_url": "/ui/user-guide", 
            "primary_button_icon": "fas fa-info-circle"
        },
        {
            "position": CTAPosition.HOME_SIDEBAR_BOTTOM,
            "title": "📍 Sidebar Bottom",
            "subtitle": "Bottom of right sidebar column", 
            "content": "<p>Great for newsletter signups or secondary actions.</p>",
            "style": CTAStyle.BORDERED,
            "background_color": "#ffffff",
            "text_color": "#495057",
            "primary_button_text": "Subscribe",
            "primary_button_url": "/ui/register",
            "primary_button_icon": "fas fa-envelope"
        }
    ]

    async for session in get_async_session():
        try:
            # Create each CTA
            created_ctas = []
            for i, cta_data in enumerate(cta_demos):
                cta = CTAContent(
                    title=cta_data["title"],
                    subtitle=cta_data["subtitle"],
                    content=cta_data["content"],
                    position=cta_data["position"],
                    style=cta_data["style"],
                    background_color=cta_data["background_color"],
                    text_color=cta_data.get("text_color", "#FFFFFF"),
                    icon_class=cta_data.get("icon_class", "fas fa-bullhorn"),
                    primary_button_text=cta_data["primary_button_text"],
                    primary_button_url=cta_data["primary_button_url"],
                    primary_button_icon=cta_data["primary_button_icon"],
                    show_for_anonymous=cta_data.get("show_for_anonymous", True),
                    show_for_authenticated=cta_data.get("show_for_authenticated", True),
                    show_for_admin=cta_data.get("show_for_admin", True),
                    sort_order=i,
                    is_active=True,
                    campaign_name=f"Demo CTA {i+1}",
                    utm_source="homepage",
                    utm_medium="cta",
                    utm_campaign=f"demo_cta_{i+1}"
                )
                
                session.add(cta)
                created_ctas.append(cta)
            
            # Commit all CTAs
            await session.commit()
            
            # Refresh to get IDs
            for cta in created_ctas:
                await session.refresh(cta)
            
            print("✅ Successfully created 11 demo CTAs:")
            for cta in created_ctas:
                print(f"   ID {cta.id}: {cta.title} ({cta.position.value})")
            
            return created_ctas
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating CTAs: {e}")
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    print("🚀 Creating 11 demo CTAs for all home page positions...")
    asyncio.run(create_demo_ctas())
    print("✅ Demo CTAs creation complete!")