"""SQLAlchemy models for cta content."""

# CTA (Call to Action) Content Model
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum

class CTAPosition(enum.Enum):
    """Enum for CTA positions on pages"""
    # Home Page Main Content Positions
    HOME_MAIN_TOP = "HOME_MAIN_TOP"
    HOME_WELCOME_TOP = "HOME_WELCOME_TOP"
    HOME_WELCOME_BOTTOM = "HOME_WELCOME_BOTTOM"
    HOME_QUICK_ACTIONS_TOP = "HOME_QUICK_ACTIONS_TOP"
    HOME_QUICK_ACTIONS_BOTTOM = "HOME_QUICK_ACTIONS_BOTTOM"
    HOME_LOGIN_REGISTER_TOP = "HOME_LOGIN_REGISTER_TOP"
    HOME_LOGIN_REGISTER_BOTTOM = "HOME_LOGIN_REGISTER_BOTTOM"
    HOME_BLOG_SECTION_TOP = "HOME_BLOG_SECTION_TOP"
    HOME_BLOG_SECTION_BOTTOM = "HOME_BLOG_SECTION_BOTTOM"
    HOME_MAIN_BOTTOM = "HOME_MAIN_BOTTOM"
    
    # Home Page Sidebar Positions
    HOME_SIDEBAR_TOP = "HOME_SIDEBAR_TOP"
    HOME_SIDEBAR_BOTTOM = "HOME_SIDEBAR_BOTTOM"
    
    # Home Page Sidebar Section Positions
    HOME_AI_CHAT_WORLDS_TOP = "HOME_AI_CHAT_WORLDS_TOP"
    HOME_AI_CHAT_WORLDS_BOTTOM = "HOME_AI_CHAT_WORLDS_BOTTOM"
    HOME_PUBLISHED_STORIES_TOP = "HOME_PUBLISHED_STORIES_TOP"
    HOME_PUBLISHED_STORIES_BOTTOM = "HOME_PUBLISHED_STORIES_BOTTOM"
    HOME_GENERATED_IMAGES_TOP = "HOME_GENERATED_IMAGES_TOP"
    HOME_GENERATED_IMAGES_BOTTOM = "HOME_GENERATED_IMAGES_BOTTOM"
    
    # Other Page Positions
    STORY_LIST_TOP = "STORY_LIST_TOP"
    WORLD_LIST_TOP = "WORLD_LIST_TOP"
    BLOG_SIDEBAR = "BLOG_SIDEBAR"
    # Add more positions as needed

class CTAStyle(enum.Enum):
    """Enum for CTA visual styles"""
    GRADIENT = "gradient"
    SOLID = "solid"
    BORDERED = "bordered"
    MINIMAL = "minimal"
    HERO = "hero"

class CTAContent(Base):
    """
    Model for storing Call to Action content in a blog-like structure.
    Allows easy management and updates through admin interface.
    """
    __tablename__ = "cta_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    title = Column(String(200), nullable=False)
    subtitle = Column(String(500))
    content = Column(Text)  # Rich text content
    
    # Positioning
    position = Column(Enum(CTAPosition), nullable=False, index=True)
    sort_order = Column(Integer, default=0)  # For multiple CTAs in same position
    
    # Visual Settings
    style = Column(Enum(CTAStyle), default=CTAStyle.GRADIENT)
    background_color = Column(String(200))  # Hex color or gradient (increased for CSS gradients)
    text_color = Column(String(50), default="#FFFFFF")
    icon_class = Column(String(100))  # FontAwesome icon class
    
    # Feature List (stored as JSON)
    features = Column(Text)  # JSON array of features with icons
    
    # Call to Action Buttons
    primary_button_text = Column(String(100))
    primary_button_url = Column(String(500))
    primary_button_icon = Column(String(50))
    
    secondary_button_text = Column(String(100))
    secondary_button_url = Column(String(500))
    secondary_button_icon = Column(String(50))
    
    # Targeting
    show_for_anonymous = Column(Boolean, default=True)
    show_for_authenticated = Column(Boolean, default=True)
    show_for_admin = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # SEO/Tracking
    campaign_name = Column(String(100))  # For analytics tracking
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    
    def to_dict(self):
        """Convert CTA content to dictionary for template rendering"""
        import json
        
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'content': self.content,
            'position': self.position.value if self.position else None,
            'style': self.style.value if self.style else 'gradient',
            'background_color': self.background_color,
            'text_color': self.text_color,
            'icon_class': self.icon_class,
            'features': json.loads(self.features) if self.features else [],
            'is_active': self.is_active,
            'sort_order': self.sort_order or 0,
            'show_for_anonymous': self.show_for_anonymous,
            'show_for_authenticated': self.show_for_authenticated,
            'show_for_admin': self.show_for_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'primary_button': {
                'text': self.primary_button_text,
                'url': self.primary_button_url,
                'icon': self.primary_button_icon
            } if self.primary_button_text else None,
            'secondary_button': {
                'text': self.secondary_button_text,
                'url': self.secondary_button_url,
                'icon': self.secondary_button_icon
            } if self.secondary_button_text else None,
            'campaign': {
                'name': self.campaign_name,
                'utm_source': self.utm_source,
                'utm_medium': self.utm_medium,
                'utm_campaign': self.utm_campaign
            } if self.campaign_name else None
        }