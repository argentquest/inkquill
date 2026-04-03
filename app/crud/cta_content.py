"""Database CRUD helpers for cta content."""

# CRUD operations for CTA Content
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.cta_content import CTAContent, CTAPosition, CTAStyle
from app.models.user import User
import json

async def create_cta_content(
    db: AsyncSession,
    title: str,
    position: CTAPosition,
    subtitle: Optional[str] = None,
    content: Optional[str] = None,
    style: str = "gradient",
    background_color: Optional[str] = None,
    text_color: str = "#FFFFFF",
    icon_class: Optional[str] = None,
    features: Optional[List[dict]] = None,
    primary_button_text: Optional[str] = None,
    primary_button_url: Optional[str] = None,
    primary_button_icon: Optional[str] = None,
    secondary_button_text: Optional[str] = None,
    secondary_button_url: Optional[str] = None,
    secondary_button_icon: Optional[str] = None,
    show_for_anonymous: bool = True,
    show_for_authenticated: bool = True,
    show_for_admin: bool = True,
    campaign_name: Optional[str] = None,
    utm_source: Optional[str] = None,
    utm_medium: Optional[str] = None,
    utm_campaign: Optional[str] = None,
    sort_order: int = 0
) -> CTAContent:
    """Create a new CTA content entry"""
    style_enum = CTAStyle(style) if isinstance(style, str) else style
    
    cta = CTAContent(
        title=title,
        subtitle=subtitle,
        content=content,
        position=position,
        style=style_enum,
        background_color=background_color,
        text_color=text_color,
        icon_class=icon_class,
        features=json.dumps(features) if features else None,
        primary_button_text=primary_button_text,
        primary_button_url=primary_button_url,
        primary_button_icon=primary_button_icon,
        secondary_button_text=secondary_button_text,
        secondary_button_url=secondary_button_url,
        secondary_button_icon=secondary_button_icon,
        show_for_anonymous=show_for_anonymous,
        show_for_authenticated=show_for_authenticated,
        show_for_admin=show_for_admin,
        campaign_name=campaign_name,
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        sort_order=sort_order,
        is_active=True
    )
    
    db.add(cta)
    await db.commit()
    await db.refresh(cta)
    return cta

async def get_cta_by_id(db: AsyncSession, cta_id: int) -> Optional[CTAContent]:
    """Get a specific CTA by ID"""
    result = await db.execute(
        select(CTAContent).where(CTAContent.id == cta_id)
    )
    return result.scalar_one_or_none()

async def get_active_ctas_for_position(
    db: AsyncSession, 
    position: CTAPosition,
    user: Optional[User] = None
) -> List[CTAContent]:
    """Get all active CTAs for a specific position, filtered by user type"""
    
    # Base query
    query = select(CTAContent).where(
        and_(
            CTAContent.position == position,
            CTAContent.is_active == True
        )
    )
    
    # Filter by user type
    if user is None:
        # Anonymous user
        query = query.where(CTAContent.show_for_anonymous == True)
    elif user.is_admin:
        # Admin user - show admin CTAs
        query = query.where(CTAContent.show_for_admin == True)
    else:
        # Authenticated non-admin user
        query = query.where(CTAContent.show_for_authenticated == True)
    
    # Order by sort_order
    query = query.order_by(CTAContent.sort_order, CTAContent.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_cta_content(
    db: AsyncSession,
    cta_id: int,
    **kwargs
) -> Optional[CTAContent]:
    """Update a CTA content entry"""
    
    cta = await get_cta_by_id(db, cta_id)
    if not cta:
        return None
    
    # Update fields
    for key, value in kwargs.items():
        if hasattr(cta, key):
            if key == 'features' and value is not None:
                value = json.dumps(value) if isinstance(value, list) else value
            elif key == "style" and isinstance(value, str):
                value = CTAStyle(value)
            setattr(cta, key, value)
    
    await db.commit()
    await db.refresh(cta)
    return cta

async def toggle_cta_active_status(
    db: AsyncSession,
    cta_id: int
) -> Optional[CTAContent]:
    """Toggle the active status of a CTA"""
    
    cta = await get_cta_by_id(db, cta_id)
    if not cta:
        return None
    
    cta.is_active = not cta.is_active
    await db.commit()
    await db.refresh(cta)
    return cta

async def delete_cta_content(
    db: AsyncSession,
    cta_id: int
) -> bool:
    """Delete a CTA content entry"""
    
    cta = await get_cta_by_id(db, cta_id)
    if not cta:
        return False
    
    await db.delete(cta)
    await db.commit()
    return True

async def get_all_ctas(
    db: AsyncSession,
    position: Optional[CTAPosition] = None,
    include_inactive: bool = False
) -> List[CTAContent]:
    """Get all CTAs, optionally filtered by position"""
    
    query = select(CTAContent)
    
    conditions = []
    if position:
        conditions.append(CTAContent.position == position)
    if not include_inactive:
        conditions.append(CTAContent.is_active == True)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(CTAContent.position, CTAContent.sort_order, CTAContent.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

# Helper function to create default CTA content
async def create_default_home_cta(db: AsyncSession) -> CTAContent:
    """Create a default CTA for the home page sidebar"""
    
    features = [
        {"icon": "fas fa-check-circle", "text": "AI-powered writing assistance", "color": "#10B981"},
        {"icon": "fas fa-check-circle", "text": "Advanced world-building tools", "color": "#10B981"},
        {"icon": "fas fa-check-circle", "text": "Publish and share your stories", "color": "#10B981"}
    ]
    
    return await create_cta_content(
        db=db,
        title="Start Your Story Today!",
        subtitle="Join thousands of writers using AI to bring their stories to life. Create rich worlds, compelling characters, and publish your masterpiece.",
        position=CTAPosition.HOME_SIDEBAR_TOP,
        style="gradient",
        background_color="linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%)",
        icon_class="fas fa-rocket",
        features=features,
        primary_button_text="Start Brainstorming",
        primary_button_url="/ui/brainstorm",
        primary_button_icon="fas fa-lightbulb",
        secondary_button_text="Sign Up Free",
        secondary_button_url="/ui/register",
        secondary_button_icon="fas fa-user-plus",
        show_for_anonymous=True,
        show_for_authenticated=True,
        campaign_name="Home Sidebar CTA",
        utm_source="homepage",
        utm_medium="sidebar",
        utm_campaign="signup"
    )
