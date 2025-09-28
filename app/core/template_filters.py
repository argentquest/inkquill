# Custom Jinja2 template filters for content sanitization
from jinja2 import Environment
from fastapi.templating import Jinja2Templates
from app.core.content_sanitizer import ContentSanitizer
from app.core.config import settings

def sanitize_html(content):
    """Jinja2 filter to sanitize HTML content"""
    return ContentSanitizer.sanitize_html_content(content)

def sanitize_text(content):
    """Jinja2 filter to sanitize text content"""
    return ContentSanitizer.sanitize_text_content(content)

def register_filters(env: Environment):
    """Register custom filters with Jinja2 environment"""
    env.filters['sanitize_html'] = sanitize_html
    env.filters['sanitize_text'] = sanitize_text

def setup_secure_templates(directory: str = "app/templates") -> Jinja2Templates:
    """
    Create a Jinja2Templates instance with security filters and standard globals.
    Use this function consistently across all routers.
    """
    templates = Jinja2Templates(directory=directory)
    
    # Add standard globals
    templates.env.globals["google_analytics_id"] = settings.GOOGLE_ANALYTICS_ID
    templates.env.globals["google_analytics_consent_mode"] = settings.GOOGLE_ANALYTICS_CONSENT_MODE
    templates.env.globals["cookie_consent_required"] = settings.COOKIE_CONSENT_REQUIRED
    
    # Register security filters
    register_filters(templates.env)
    
    return templates