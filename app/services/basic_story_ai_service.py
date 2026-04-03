"""Service helpers for basic story ai service."""

# /story_app/app/services/basic_story_ai_service.py

import time
import logging
from typing import Optional, Dict, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story import Story
from app.models.user import User
from app.services.story_service import story_service
from app.services.ai_model_cache import model_cache
from app.services.semantic_kernel_setup import kernel

logger = logging.getLogger(__name__)


class BasicStoryAIService:
    """
    AI service specifically for Basic Stories with context-free prompts and proper logging.
    """
    
    def __init__(self):
        self.kernel = None
    
    async def get_semantic_kernel(self):
        """Get or initialize Semantic Kernel"""
        if not self.kernel:
            self.kernel = kernel
        return self.kernel
    
    async def get_writing_assistance(
        self,
        db: AsyncSession,
        story: Story,
        user: User,
        story_content: str,
        assistance_type: str = "general",
        specific_request: Optional[str] = None,
        model_id: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Get AI writing assistance for Basic Stories.
        
        Args:
            db: Database session
            story: Basic Story instance
            user: User requesting assistance
            story_content: Current story content
            assistance_type: Type of assistance needed
            specific_request: Specific user request
            
        Yields:
            Streaming AI response chunks
        """
        if not story_service.is_basic_story(story):
            raise ValueError("This service is only for Basic Stories")
        
        start_time = time.time()
        accumulated_output = ""
        
        try:
            # Get AI model configuration
            if model_id and user.is_admin:
                # Admin can use selected model
                from app.crud.ai_model_config import get_model_config_by_id
                # Convert string model_id to integer
                try:
                    model_id_int = int(model_id)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid model ID: {model_id}")
                
                model_config = await get_model_config_by_id(db, model_id_int)
                if not model_config:
                    raise ValueError(f"Model with ID {model_id} not found")
            else:
                # Non-admin users use public chat default model
                from app.crud.ai_model_config import get_public_chat_default_model_config
                model_config = await get_public_chat_default_model_config(db)
                if not model_config:
                    raise ValueError("No public chat default model available")
            
            # Get Semantic Kernel
            kernel = await self.get_semantic_kernel()
            
            # Prepare prompt variables without external document retrieval for Basic Stories
            prompt_variables = story_service.get_basic_story_prompt_variables(
                story=story,
                content=story_content,
                assistance_type=assistance_type,
                specific_request=specific_request or "",
                current_scene=story_content[-1000:] if len(story_content) > 1000 else story_content  # Use last 1000 chars as current scene
            )
            
            # Use appropriate Basic Story prompt
            prompt_name = self._get_prompt_name_for_assistance_type(assistance_type)
            
            # Build full input prompt for logging
            input_prompt = self._build_input_prompt(prompt_variables, assistance_type)
            
            # Call AI with Basic Story prompt
            function = kernel.get_function("basic_story", prompt_name)
            
            # Stream the response
            async for stream_item in function.invoke_stream(kernel, **prompt_variables):
                chunk_text = str(stream_item[0]) if stream_item else ""
                if chunk_text:
                    accumulated_output += chunk_text
                    yield chunk_text
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log the AI call with cost tracking
            await story_service.log_basic_story_ai_call(
                db=db,
                user_id=user.id,
                model_config=model_config,
                prompt_type=assistance_type,
                input_prompt=input_prompt,
                output_text=accumulated_output,
                story_id=story.id,
                duration_ms=duration_ms
            )
            
            logger.info(f"Basic Story AI assistance completed: {assistance_type} for story {story.id}")
            
        except Exception as e:
            logger.error(f"Error in Basic Story AI assistance: {e}")
            
            # Still log the call even if it failed (for cost tracking)
            if 'model_config' in locals() and accumulated_output:
                duration_ms = int((time.time() - start_time) * 1000)
                await story_service.log_basic_story_ai_call(
                    db=db,
                    user_id=user.id,
                    model_config=model_config,
                    prompt_type=f"{assistance_type}_error",
                    input_prompt=input_prompt if 'input_prompt' in locals() else "",
                    output_text=accumulated_output,
                    story_id=story.id,
                    duration_ms=duration_ms
                )
            
            raise
    
    async def get_story_continuation_suggestions(
        self,
        db: AsyncSession,
        story: Story,
        user: User,
        current_content: str,
        num_suggestions: int = 3
    ) -> list[str]:
        """
        Get suggestions for continuing the story.
        
        Args:
            db: Database session
            story: Basic Story instance
            user: User requesting suggestions
            current_content: Current story content
            num_suggestions: Number of suggestions to generate
            
        Returns:
            List of continuation suggestions
        """
        suggestions = []
        
        async for chunk in self.get_writing_assistance(
            db=db,
            story=story,
            user=user,
            story_content=current_content,
            assistance_type="what_happens_next",
            specific_request=f"Provide {num_suggestions} specific suggestions"
        ):
            # Accumulate chunks for suggestions
            pass  # The actual suggestion parsing would happen here
        
        # For now, return placeholder suggestions
        # In real implementation, you'd parse the AI response
        return [
            "Suggestion 1 based on AI response",
            "Suggestion 2 based on AI response", 
            "Suggestion 3 based on AI response"
        ]
    
    def _get_prompt_name_for_assistance_type(self, assistance_type: str) -> str:
        """Map assistance types to prompt file names"""
        prompt_mapping = {
            "general": "basic_writing_assistance",
            "continue": "continue_story",
            "what_happens_next": "what_happens_next",
            "dialogue": "improve_dialogue",
            "improve": "writing_feedback",  # Map to writing_feedback.txt
            "plot_twist": "plot_brainstorm",  # Map to plot_brainstorm.txt
            "character_dev": "character_voice_development",  # Map to character_voice_development.txt
            "scene": "scene_development",
            "plot": "plot_brainstorm",
            "feedback": "writing_feedback",
            "creative": "creative_brainstorm",
            "problem": "story_problem_solver",
            "character_voice": "character_voice_development",
            "emotional": "emotional_development"
        }
        return prompt_mapping.get(assistance_type, "basic_writing_assistance")
    
    def _build_input_prompt(self, variables: Dict[str, str], assistance_type: str) -> str:
        """Build a readable input prompt for logging purposes"""
        prompt_parts = [
            f"Basic Story AI Assistance: {assistance_type}",
            f"Story: {variables.get('story_title', 'Untitled')}",
            f"Content Length: {len(variables.get('story_content', ''))} characters"
        ]
        
        if variables.get('specific_request'):
            prompt_parts.append(f"Request: {variables['specific_request']}")
        
        return "\n".join(prompt_parts)


# Global service instance
basic_story_ai_service = BasicStoryAIService()

