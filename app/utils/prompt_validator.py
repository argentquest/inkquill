# /ai_rag_story_app/app/utils/prompt_validator.py

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class PromptValidator:
    """Validates and sanitizes prompts for DALL-E 3 image generation"""
    
    # Known problematic patterns that cause 400 errors
    PROHIBITED_PATTERNS = [
        r'\b(violence|violent|gore|blood|death|kill|murder)\b',
        r'\b(nude|naked|nsfw|explicit)\b',
        r'\b(drug|alcohol|intoxicated)\b',
        r'\b(hate|racist|discrimination)\b',
        r'\b(celebrity|politician|public figure)\b',
    ]
    
    # Minimum and maximum lengths
    MIN_LENGTH = 10
    MAX_LENGTH = 1000
    
    @staticmethod
    def validate_and_clean(prompt: str, element_type: str = "image") -> Tuple[bool, str, Optional[str]]:
        """
        Validate and clean a prompt for DALL-E 3
        
        Args:
            prompt: The raw prompt text
            element_type: Type of element (character, location, etc.) for context
            
        Returns:
            Tuple of (is_valid, cleaned_prompt, error_message)
        """
        
        if not prompt or not prompt.strip():
            fallback = PromptValidator._get_fallback_prompt(element_type)
            return True, fallback, "Empty prompt, using fallback"
        
        # Basic cleaning
        cleaned = prompt.strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
        
        # Remove any HTML/XML tags
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Check for prohibited content
        for pattern in PromptValidator.PROHIBITED_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                logger.warning(f"Prompt contains prohibited content matching pattern: {pattern}")
                fallback = PromptValidator._get_fallback_prompt(element_type)
                return True, fallback, f"Prompt contained prohibited content, using safe fallback"
        
        # Remove problematic endings
        cleaned = PromptValidator._fix_incomplete_sentences(cleaned)
        
        # Length validation
        if len(cleaned) < PromptValidator.MIN_LENGTH:
            fallback = PromptValidator._get_fallback_prompt(element_type)
            return True, fallback, "Prompt too short, using fallback"
        
        if len(cleaned) > PromptValidator.MAX_LENGTH:
            cleaned = PromptValidator._truncate_intelligently(cleaned)
        
        # Final validation
        if not cleaned or len(cleaned) < PromptValidator.MIN_LENGTH:
            fallback = PromptValidator._get_fallback_prompt(element_type)
            return True, fallback, "Prompt invalid after cleaning, using fallback"
        
        logger.info(f"Prompt validated successfully. Length: {len(cleaned)}")
        return True, cleaned, None
    
    @staticmethod
    def _fix_incomplete_sentences(text: str) -> str:
        """Fix common incomplete sentence issues"""
        
        # Remove trailing incomplete words
        text = re.sub(r'\s+\w{1,3}$', '', text)
        
        # Fix incomplete parentheses
        open_parens = text.count('(')
        close_parens = text.count(')')
        if open_parens > close_parens:
            text = re.sub(r'\([^)]*$', '', text)
        
        # Remove trailing punctuation issues
        text = re.sub(r'[,\s\(]+$', '', text)
        
        # Ensure ends with proper punctuation
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text
    
    @staticmethod
    def _truncate_intelligently(text: str) -> str:
        """Truncate text at a sentence boundary"""
        
        max_len = PromptValidator.MAX_LENGTH
        if len(text) <= max_len:
            return text
        
        # Try to find a sentence boundary
        truncated = text[:max_len]
        
        # Look for last sentence ending
        for punct in ['. ', '! ', '? ']:
            last_punct = truncated.rfind(punct)
            if last_punct > max_len * 0.7:  # Keep at least 70% of max length
                return truncated[:last_punct + 1].strip()
        
        # If no good boundary, truncate at word
        last_space = truncated.rfind(' ')
        if last_space > max_len * 0.8:
            return truncated[:last_space].strip() + '...'
        
        return truncated.strip() + '...'
    
    @staticmethod
    def _get_fallback_prompt(element_type: str) -> str:
        """Get a safe fallback prompt based on element type"""
        
        fallbacks = {
            "character": "A fantasy character portrait in artistic style, suitable for a story",
            "location": "A fantasy landscape with mystical atmosphere, suitable for storytelling",
            "lore_item": "A magical artifact or mystical item, detailed and artistic",
            "scene": "An artistic scene from a fantasy story, atmospheric and engaging",
            "story": "A fantasy book cover illustration, artistic and engaging",
            "world": "A fantasy world map or landscape, detailed and imaginative",
            "image": "A beautiful artistic image in fantasy style"
        }
        
        return fallbacks.get(element_type, fallbacks["image"])