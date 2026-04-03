"""Application package for the Ink and Quill backend."""

# /story_app/app/utils/social_media_utils.py

from typing import Optional, Dict, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class SocialMediaMetaGenerator:
    """Utility class for generating social media meta tags dynamically"""
    
    @staticmethod
    def generate_story_meta(story: Any, request: Any = None) -> Dict[str, str]:
        """Generate Open Graph meta tags for a story"""
        
        # Base URL for absolute URLs
        base_url = str(request.base_url) if request else ""
        
        # Story title - fallback hierarchy
        title = getattr(story, 'title', None) or "Untitled Story"
        
        # Story description - try multiple fields
        description = (
            getattr(story, 'summary', None) or 
            getattr(story, 'description', None) or 
            "Discover an engaging story created with AI assistance on our storytelling platform."
        )
        
        # Story image - try multiple sources
        image_url = None
        if hasattr(story, 'image_url') and story.image_url:
            image_url = story.image_url
        elif hasattr(story, 'world') and story.world and hasattr(story.world, 'image_url') and story.world.image_url:
            image_url = story.world.image_url
        else:
            # Fallback to logo
            if request:
                image_url = str(request.url_for('static', path='/images/logo.jpeg'))
            else:
                image_url = '/static/images/logo.jpeg'
        
        # Ensure absolute URL for image
        if image_url and not image_url.startswith('http'):
            image_url = urljoin(base_url, image_url)
        
        # Current page URL
        current_url = str(request.url) if request else ""
        
        # Additional keywords
        keywords = ["story", title, "creative writing", "AI storytelling"]
        if hasattr(story, 'world') and story.world and hasattr(story.world, 'name'):
            keywords.append(story.world.name)
        
        return {
            'og:type': 'article',
            'og:title': title,
            'og:description': description[:300] + "..." if len(description) > 300 else description,
            'og:image': image_url,
            'og:url': current_url,
            'og:site_name': 'AI Storytelling Assistant',
            'twitter:card': 'summary_large_image',
            'twitter:title': title,
            'twitter:description': description[:200] + "..." if len(description) > 200 else description,
            'twitter:image': image_url,
            'meta:description': description[:160] + "..." if len(description) > 160 else description,
            'meta:keywords': ", ".join(keywords)
        }
    
    @staticmethod
    def generate_world_meta(world: Any, request: Any = None) -> Dict[str, str]:
        """Generate Open Graph meta tags for a world"""
        
        base_url = str(request.base_url) if request else ""
        
        title = getattr(world, 'name', None) or "Untitled World"
        description = (
            getattr(world, 'description', None) or 
            "Explore this immersive world created with AI assistance on our storytelling platform."
        )
        
        # World image
        image_url = None
        if hasattr(world, 'image_url') and world.image_url:
            image_url = world.image_url
        else:
            if request:
                image_url = str(request.url_for('static', path='/images/logo.jpeg'))
            else:
                image_url = '/static/images/logo.jpeg'
        
        if image_url and not image_url.startswith('http'):
            image_url = urljoin(base_url, image_url)
        
        current_url = str(request.url) if request else ""
        
        keywords = ["world building", title, "creative writing", "AI storytelling", "fantasy world"]
        
        return {
            'og:type': 'article',
            'og:title': title,
            'og:description': description[:300] + "..." if len(description) > 300 else description,
            'og:image': image_url,
            'og:url': current_url,
            'og:site_name': 'AI Storytelling Assistant',
            'twitter:card': 'summary_large_image',
            'twitter:title': title,
            'twitter:description': description[:200] + "..." if len(description) > 200 else description,
            'twitter:image': image_url,
            'meta:description': description[:160] + "..." if len(description) > 160 else description,
            'meta:keywords': ", ".join(keywords)
        }
    
    @staticmethod
    def generate_published_story_meta(published_story: Any, request: Any = None) -> Dict[str, str]:
        """Generate Open Graph meta tags for a published story"""
        
        base_url = str(request.base_url) if request else ""
        
        title = getattr(published_story, 'title', None) or "Published Story"
        description = (
            getattr(published_story, 'description', None) or 
            "Read this engaging story published on our AI storytelling platform."
        )
        
        # Try to get image from story or world
        image_url = None
        if (hasattr(published_story, 'story') and published_story.story and 
            hasattr(published_story.story, 'image_url') and published_story.story.image_url):
            image_url = published_story.story.image_url
        elif (hasattr(published_story, 'story') and published_story.story and 
              hasattr(published_story.story, 'world') and published_story.story.world and
              hasattr(published_story.story.world, 'image_url') and published_story.story.world.image_url):
            image_url = published_story.story.world.image_url
        else:
            if request:
                image_url = str(request.url_for('static', path='/images/logo.jpeg'))
            else:
                image_url = '/static/images/logo.jpeg'
        
        if image_url and not image_url.startswith('http'):
            image_url = urljoin(base_url, image_url)
        
        current_url = str(request.url) if request else ""
        
        keywords = ["published story", title, "creative writing", "AI storytelling"]
        if (hasattr(published_story, 'story') and published_story.story and 
            hasattr(published_story.story, 'world') and published_story.story.world):
            keywords.append(published_story.story.world.name)
        
        return {
            'og:type': 'article',
            'og:title': title,
            'og:description': description[:300] + "..." if len(description) > 300 else description,
            'og:image': image_url,
            'og:url': current_url,
            'og:site_name': 'AI Storytelling Assistant',
            'twitter:card': 'summary_large_image',
            'twitter:title': title,
            'twitter:description': description[:200] + "..." if len(description) > 200 else description,
            'twitter:image': image_url,
            'meta:description': description[:160] + "..." if len(description) > 160 else description,
            'meta:keywords': ", ".join(keywords)
        }

def generate_preview_image_url(content_type: str, content_id: int, request: Any = None) -> str:
    """Generate URL for a dynamic preview image"""
    if request:
        return str(request.url_for('generate_social_preview', content_type=content_type, content_id=content_id))
    else:
        return f"/api/v1/social/preview/{content_type}/{content_id}.jpg"
