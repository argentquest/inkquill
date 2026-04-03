"""Core application helpers for content sanitizer."""

# Content sanitization utilities to prevent XSS and malicious content injection
import re
import logging
from typing import Optional
from html import escape

logger = logging.getLogger(__name__)

class ContentSanitizer:
    """
    Sanitizes HTML content to prevent XSS attacks and malicious iframe embedding.
    """
    
    # List of dangerous domains to block
    BLOCKED_DOMAINS = [
        'bedpage.com',
        'backpage.com',
        'adultfriendfinder.com',
        # Add more suspicious domains as needed
    ]
    
    # Dangerous HTML tags to remove
    DANGEROUS_TAGS = [
        'iframe', 'frame', 'frameset', 'object', 'embed', 'applet',
        'script', 'noscript', 'style', 'link', 'meta', 'base',
        'form', 'input', 'button', 'textarea', 'select', 'option'
    ]
    
    @classmethod
    def sanitize_html_content(cls, content: Optional[str]) -> Optional[str]:
        """
        Sanitize HTML content by removing dangerous tags and blocked domains.
        
        Args:
            content: The HTML content to sanitize
            
        Returns:
            Sanitized content or None if content is None
        """
        if not content:
            return content
            
        original_content = content
        
        try:
            # Convert to lowercase for case-insensitive matching
            content_lower = content.lower()
            
            # Check for blocked domains
            for domain in cls.BLOCKED_DOMAINS:
                if domain in content_lower:
                    logger.critical(f"SECURITY ALERT: Blocked malicious domain '{domain}' in content")
                    # Replace the entire content with a safe message
                    return "<p><strong>Content blocked for security reasons.</strong></p>"
            
            # Remove dangerous HTML tags using regex
            for tag in cls.DANGEROUS_TAGS:
                # Remove opening and closing tags (case insensitive)
                pattern = rf'<\s*{tag}[^>]*>.*?<\s*/\s*{tag}\s*>'
                content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
                
                # Remove self-closing tags
                pattern = rf'<\s*{tag}[^/>]*/?>'
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            # Remove any remaining iframe-like content
            iframe_patterns = [
                r'<iframe[^>]*>.*?</iframe>',
                r'<frame[^>]*>.*?</frame>',
                r'<object[^>]*>.*?</object>',
                r'<embed[^>]*/?>'
            ]
            
            for pattern in iframe_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove dangerous attributes from remaining tags
            dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur']
            for attr in dangerous_attrs:
                pattern = rf'{attr}\s*=\s*["\'][^"\']*["\']'
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            # Log if content was modified
            if content != original_content:
                logger.warning("Content was sanitized - potentially malicious content removed")
                
            return content
            
        except Exception as e:
            logger.error(f"Error sanitizing content: {e}")
            # Return escaped content as fallback
            return escape(original_content) if original_content else None
    
    @classmethod
    def sanitize_text_content(cls, content: Optional[str]) -> Optional[str]:
        """
        Sanitize plain text content by checking for malicious URLs.
        
        Args:
            content: The text content to sanitize
            
        Returns:
            Sanitized content or None if content is None
        """
        if not content:
            return content
            
        try:
            content_lower = content.lower()
            
            # Check for blocked domains in URLs
            for domain in cls.BLOCKED_DOMAINS:
                if domain in content_lower:
                    logger.critical(f"SECURITY ALERT: Blocked malicious domain '{domain}' in text content")
                    # Replace the domain with [BLOCKED]
                    content = re.sub(
                        re.escape(domain), 
                        '[BLOCKED_DOMAIN]', 
                        content, 
                        flags=re.IGNORECASE
                    )
            
            return content
            
        except Exception as e:
            logger.error(f"Error sanitizing text content: {e}")
            return content
    
    @classmethod
    def is_content_safe(cls, content: Optional[str]) -> bool:
        """
        Check if content is safe without modifying it.
        
        Args:
            content: The content to check
            
        Returns:
            True if content is safe, False otherwise
        """
        if not content:
            return True
            
        content_lower = content.lower()
        
        # Check for blocked domains
        for domain in cls.BLOCKED_DOMAINS:
            if domain in content_lower:
                return False
        
        # Check for dangerous tags
        for tag in cls.DANGEROUS_TAGS:
            if f'<{tag}' in content_lower:
                return False
                
        return True