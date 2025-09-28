"""Blog AI prompt loading service."""
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class BlogPromptService:
    """Service for loading blog AI prompts from text files."""
    
    _prompts: Dict[str, str] = {}
    _prompts_dir = Path(__file__).parent.parent / "prompts" / "blog_ai"
    
    @classmethod
    def load_prompt(cls, prompt_name: str) -> Optional[str]:
        """Load a prompt from file, with caching."""
        if prompt_name in cls._prompts:
            return cls._prompts[prompt_name]
        
        prompt_file = cls._prompts_dir / f"{prompt_name}.txt"
        if not prompt_file.exists():
            logger.error(f"Blog prompt file not found: {prompt_file}")
            return None
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()
            
            cls._prompts[prompt_name] = prompt_content
            logger.debug(f"Loaded blog prompt: {prompt_name}")
            return prompt_content
        
        except Exception as e:
            logger.error(f"Error loading blog prompt {prompt_name}: {e}")
            return None
    
    @classmethod
    def format_content_generation_prompt(
        cls,
        topic: str,
        style: str = "informative",
        length: str = "medium",
        category: str = "",
        existing_content: str = "",
        context_parts: list = None
    ) -> Optional[str]:
        """Format the content generation prompt with parameters."""
        template = cls.load_prompt("generate_content")
        if not template:
            return None
        
        # Style guide mapping
        style_guide = {
            "informative": "educational and informative style",
            "conversational": "friendly and conversational tone",
            "professional": "professional and authoritative tone",
            "creative": "creative and engaging style",
            "tutorial": "step-by-step tutorial format"
        }
        
        # Length guide mapping
        length_guide = {
            "short": "Write a concise blog post (300-500 words)",
            "medium": "Write a medium-length blog post (600-1000 words)",
            "long": "Write a comprehensive blog post (1200-2000 words)"
        }
        
        # Build optional parts
        category_focus = f"Category focus: {category}" if category else ""
        existing_content_part = f"Build upon this existing content:\n{existing_content}" if existing_content else ""
        context = "\n".join(context_parts) if context_parts else ""
        
        return template.format(
            topic=topic,
            style=style_guide.get(style, style),
            length_guide=length_guide.get(length, "medium-length"),
            category_focus=category_focus,
            existing_content=existing_content_part,
            context=context
        )
    
    @classmethod
    def format_improve_writing_prompt(
        cls,
        content: str,
        improvement_type: str = "general"
    ) -> Optional[str]:
        """Format the improve writing prompt with parameters."""
        template = cls.load_prompt("improve_writing")
        if not template:
            return None
        
        improvement_prompts = {
            "general": "Improve the overall quality, clarity, and engagement of this blog content:",
            "grammar": "Fix grammar, spelling, and writing mechanics in this blog content:",
            "seo": "Optimize this blog content for SEO and readability:",
            "engagement": "Make this blog content more engaging and compelling:",
            "structure": "Improve the structure and flow of this blog content:",
            "tone": "Adjust the tone to be more professional and polished:"
        }
        
        improvement_instruction = improvement_prompts.get(improvement_type, improvement_prompts['general'])
        
        return template.format(
            improvement_instruction=improvement_instruction,
            content=content
        )
    
    @classmethod
    def format_generate_title_prompt(
        cls,
        content: str = "",
        topic: str = "",
        style: str = "engaging"
    ) -> Optional[str]:
        """Format the generate title prompt with parameters."""
        template = cls.load_prompt("generate_title")
        if not template:
            return None
        
        source_text = content if content else f"Topic: {topic}"
        
        return template.format(
            source_text=source_text,
            style=style
        )
    
    @classmethod
    def format_generate_excerpt_prompt(cls, content: str, max_length: int = 200) -> Optional[str]:
        """Format the generate excerpt prompt with parameters."""
        template = cls.load_prompt("generate_excerpt")
        if not template:
            return None
        
        return template.format(content=content, max_length=max_length)
    
    @classmethod
    def format_suggest_tags_prompt(
        cls,
        content: str = "",
        title: str = "",
        existing_tags: list = None
    ) -> Optional[str]:
        """Format the suggest tags prompt with parameters."""
        template = cls.load_prompt("suggest_tags")
        if not template:
            return None
        
        source_text = f"Title: {title}\n\nContent: {content}" if title else content
        existing_tags_str = ', '.join(existing_tags[:50]) if existing_tags else ""
        
        return template.format(
            source_text=source_text,
            existing_tags=existing_tags_str
        )
    
    @classmethod
    def format_writing_tips_prompt(
        cls,
        content: str = "",
        tip_type: str = "general"
    ) -> Optional[str]:
        """Format the writing tips prompt with parameters."""
        template = cls.load_prompt("writing_tips")
        if not template:
            return None
        
        tip_prompts = {
            "general": "Provide 3-5 general blog writing tips to improve engagement and readability.",
            "seo": "Provide 3-5 SEO optimization tips for blog posts.",
            "structure": "Provide 3-5 tips for improving blog post structure and flow.",
            "headlines": "Provide 3-5 tips for writing compelling blog headlines.",
            "introduction": "Provide 3-5 tips for writing engaging blog introductions.",
            "conclusion": "Provide 3-5 tips for writing effective blog conclusions."
        }
        
        tip_instruction = tip_prompts.get(tip_type, tip_prompts['general'])
        
        if content:
            content_analysis = f"Analyze this blog content and provide specific writing tips:\n\n{content}\n\n"
        else:
            content_analysis = ""
        
        return template.format(
            content_analysis=content_analysis,
            tip_instruction=tip_instruction
        )
    
    @classmethod
    def get_enhancement_prompt(cls, enhancement_type: str) -> Optional[str]:
        """Get enhancement prompt for different enhancement types."""
        enhancement_map = {
            "improve": "enhance_improve",
            "expand": "enhance_expand", 
            "rewrite": "enhance_rewrite",
            "continue": "enhance_continue"
        }
        
        prompt_name = enhancement_map.get(enhancement_type, "enhance_improve")
        return cls.load_prompt(prompt_name)
    
    @classmethod
    def format_title_suggestions_prompt(cls, content: str, count: int = 5) -> Optional[str]:
        """Format the title suggestions prompt with parameters."""
        template = cls.load_prompt("generate_title_suggestions")
        if not template:
            return None
        
        return template.format(count=count)
    
    @classmethod
    def format_tags_generation_prompt(cls) -> Optional[str]:
        """Format the tags generation prompt."""
        return cls.load_prompt("generate_tags")
    
    @classmethod
    def format_excerpt_generation_prompt(cls, max_length: int = 200) -> Optional[str]:
        """Format the excerpt generation prompt with parameters."""
        template = cls.load_prompt("generate_excerpt")
        if not template:
            return None
        
        return template.format(max_length=max_length)