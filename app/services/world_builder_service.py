"""World Builder Service

This service handles the world building wizard functionality, including:
- Loading and managing world building questions
- Processing user answers
- Generating AI world descriptions from answers
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.world import World
from app.schemas.world import WorldCreate, WorldUpdate
from app.crud import world as crud_world
from app.services.cost_tracker_service import log_ai_call, estimate_tokens_for_streaming_call
from app.services.ai_model_cache import model_cache

logger = logging.getLogger(__name__)


class WorldBuilderService:
    """Service for the world building wizard"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data" / "world_builder"
        self._questions_cache = None
        self._load_questions()
    
    def _load_questions(self):
        """Load world builder questions from JSON file"""
        try:
            questions_file = self.data_path / "questions.json"
            with open(questions_file, 'r') as f:
                data = json.load(f)
                self._questions_cache = data.get("questions", [])
            logger.info(f"Loaded {len(self._questions_cache)} world builder questions")
        except Exception as e:
            logger.error(f"Failed to load world builder questions: {e}")
            self._questions_cache = []
    
    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Get all world builder questions"""
        return self._questions_cache.copy() if self._questions_cache else []
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific question by ID"""
        for question in self._questions_cache:
            if question.get("id") == question_id:
                return question.copy()
        return None
    
    def validate_answers(self, answers: Dict[int, int]) -> Tuple[bool, List[str]]:
        """
        Validate that the provided answers are valid
        
        Args:
            answers: Dict mapping question_id to answer_id
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not answers:
            errors.append("No answers provided")
            return False, errors
        
        # Check each answer
        for question_id, answer_id in answers.items():
            question = self.get_question_by_id(question_id)
            if not question:
                errors.append(f"Invalid question ID: {question_id}")
                continue
            
            # Check if answer_id is valid for this question
            valid_answer_ids = [a["id"] for a in question.get("answers", [])]
            if answer_id not in valid_answer_ids:
                errors.append(f"Invalid answer ID {answer_id} for question {question_id}")
        
        return len(errors) == 0, errors
    
    def format_answers_for_prompt(self, answers: Dict[int, int]) -> str:
        """Format user answers into a structured prompt for AI generation"""
        formatted_parts = []
        
        for question_id, answer_id in sorted(answers.items()):
            question = self.get_question_by_id(question_id)
            if not question:
                continue
            
            # Find the selected answer
            selected_answer = None
            for answer in question.get("answers", []):
                if answer["id"] == answer_id:
                    selected_answer = answer
                    break
            
            if selected_answer:
                formatted_parts.append(
                    f"{question['short_label']}: {selected_answer['text']}"
                )
        
        return "\n".join(formatted_parts)
    
    async def generate_world_description(
        self,
        answers: Dict[int, int],
        user_id: int,
        db: AsyncSession
    ) -> Dict[str, str]:
        """
        Generate AI world descriptions (short and long) from user answers
        
        Returns:
            Dict with 'short_description', 'description', and 'visual_prompt' keys
        """
        try:
            # Format answers for AI prompt
            formatted_answers = self.format_answers_for_prompt(answers)
            
            # Import storytelling runtime components
            from app.services.storytelling_runtime import kernel
            from app.services.langgraph_kernel import KernelArguments, OpenAIChatPromptExecutionSettings, PromptTemplateConfig
            from app.core.config import settings
            
            # Create the world generation prompt
            world_context = {
                "answers": formatted_answers,
                "instruction": "Generate a compelling world description based on these characteristics"
            }
            
            # Define the AI generation prompt
            prompt_template = """Based on the following world-building choices, create compelling descriptions:

{{$answers}}

Please generate:
1. A SHORT DESCRIPTION (1-2 sentences, maximum 50 words) that captures the essence of this world
2. A LONGER DESCRIPTION (3-5 paragraphs) that expands on the world's key features, atmosphere, and what makes it unique
3. A VISUAL PROMPT (1-2 sentences) optimized for image generation that describes the world's visual appearance

Format your response as:
SHORT: [short description here]
LONG: [longer description here]
VISUAL: [visual prompt here]"""

            # Use the correct service ID that's registered in the kernel
            chat_service_id = "chat_service"
            
            # Create execution settings
            exec_settings = OpenAIChatPromptExecutionSettings(
                service_id=chat_service_id,
                max_tokens=settings.AI_MAX_TOKEN_SETTINGS.get("general", 2000),
                temperature=settings.AI_TEMPERATURE_SETTINGS.get("general", 0.7),
                top_p=settings.AI_TOP_P_SETTINGS.get("general", 0.9)
            )
            
            # Create prompt config
            prompt_config = PromptTemplateConfig(
                template=prompt_template,
                name="generate_world_description",
                template_format="semantic-kernel",
                description="Generate world descriptions from builder answers",
                input_variables=[
                    {"name": "answers", "description": "Formatted user answers", "is_required": True}
                ],
                execution_settings={chat_service_id: exec_settings}
            )
            
            # Add function to kernel (temporarily for this call)
            function_name = "generate_world_description"
            plugin_name = "WorldBuilderTemp"
            
            kernel.add_function(
                function_name=function_name,
                plugin_name=plugin_name,
                prompt_template_config=prompt_config
            )
            
            # Execute AI generation
            kernel_args = KernelArguments(**world_context)
            world_generation_function = kernel.plugins[plugin_name][function_name]
            result = await kernel.invoke(world_generation_function, kernel_args)
            
            # Parse the result - handle ChatMessageContent properly
            result_text = ""
            content_filter_results = None
            
            if result and result.value:
                # Check if result.value is a ChatMessageContent object
                if hasattr(result.value, 'content'):
                    result_text = str(result.value.content)
                else:
                    # Check if it's wrapped in another object
                    if isinstance(result.value, list) and len(result.value) > 0:
                        if hasattr(result.value[0], 'content'):
                            result_text = str(result.value[0].content)
                        else:
                            result_text = str(result.value[0])
                    else:
                        result_text = str(result.value)
                
                # Extract content filter results if available
                if hasattr(result.value, 'metadata') and 'content_filter_results' in result.value.metadata:
                    content_filter_results = result.value.metadata['content_filter_results']
                    logger.info(f"Content filter results: {content_filter_results}")
            
            # Clean up any JSON artifacts from the text
            if '[ChatMessageContent(' in result_text:
                # Extract just the content part
                import re
                content_match = re.search(r'content="([^"]*)"', result_text)
                if content_match:
                    result_text = content_match.group(1)
            
            # Replace literal \n with actual newlines
            result_text = result_text.replace('\\n\\n', '\n\n').replace('\\n', '\n')
            
            # Extract the three parts
            short_desc = ""
            long_desc = ""
            visual_prompt = ""
            
            if "SHORT:" in result_text and "LONG:" in result_text:
                parts = result_text.split("LONG:")
                short_part = parts[0].replace("SHORT:", "").strip()
                
                if "VISUAL:" in parts[1]:
                    long_visual_parts = parts[1].split("VISUAL:")
                    long_desc = long_visual_parts[0].strip()
                    visual_prompt = long_visual_parts[1].strip()
                else:
                    long_desc = parts[1].strip()
                
                short_desc = short_part
            else:
                # Fallback parsing
                lines = result_text.split('\n')
                if lines:
                    short_desc = lines[0][:200]  # First line, max 200 chars
                    long_desc = '\n'.join(lines[1:]) if len(lines) > 1 else lines[0]
                    visual_prompt = f"A panoramic view of {short_desc.lower()}"
            
            # Ensure we have valid descriptions
            if not short_desc:
                short_desc = "A unique world with diverse characteristics and rich potential for storytelling."
            if not long_desc:
                long_desc = short_desc + "\n\nThis world offers endless possibilities for adventure and discovery."
            if not visual_prompt:
                visual_prompt = "A sweeping landscape view of a fantastical world, highly detailed, atmospheric"
            
            # Log AI cost
            try:
                model_config = model_cache.default_generation_model
                if model_config:
                    # Estimate tokens since we're using streaming
                    input_text = prompt_template.replace("{{$answers}}", formatted_answers)
                    usage_data = estimate_tokens_for_streaming_call(
                        input_text=input_text,
                        output_text=result_text,
                        model_name=model_config.model_name
                    )
                    
                    await log_ai_call(
                        user_id=user_id,
                        model_config=model_config,
                        usage=usage_data,
                        call_type="world_builder_generation",
                        input_prompt=f"World Builder: {len(answers)} answers provided",
                        duration_ms=500,  # Approximate
                        object_id=None,
                        db=db
                    )
            except Exception as cost_error:
                logger.error(f"Failed to log AI cost for world generation: {cost_error}")
            
            # Log content filter results if available
            if content_filter_results:
                logger.info(f"Content filter results for world generation: {content_filter_results}")
            
            return {
                "short_description": short_desc[:500],  # Ensure max length
                "description": long_desc,
                "visual_prompt": visual_prompt[:500],  # Ensure max length
                "content_filter_results": content_filter_results  # Include filter results
            }
            
        except Exception as e:
            logger.error(f"Failed to generate world description: {e}")
            # Return fallback descriptions
            return {
                "short_description": "A world shaped by unique choices and infinite possibilities.",
                "description": "This world represents a unique blend of characteristics, offering a rich tapestry for storytelling and adventure. Its distinctive features create an environment where anything is possible.",
                "visual_prompt": "A fantastical world landscape with unique features, atmospheric and detailed",
                "content_filter_results": None
            }
    
    async def create_world_from_builder(
        self,
        user_id: int,
        world_name: str,
        answers: Dict[int, int],
        generated_content: Dict[str, str],
        db: AsyncSession
    ) -> World:
        """
        Create a new world from world builder data
        
        Args:
            user_id: ID of the user creating the world
            world_name: Name for the new world
            answers: Dict mapping question_id to answer_id
            generated_content: Dict with AI-generated descriptions
            db: Database session
            
        Returns:
            Created World object
        """
        # Prepare world builder data
        world_builder_data = {
            "answers": answers,
            "questions_version": "1.0",  # Track version for future updates
            "completed_at": str(datetime.datetime.now(datetime.UTC))
        }
        
        # Create world data
        world_data = WorldCreate(
            name=world_name,
            description=generated_content.get("description", ""),
            short_description=generated_content.get("short_description", ""),
            image_prompt_definition=generated_content.get("visual_prompt", ""),
            world_builder_data=world_builder_data
        )
        
        # Create the world
        world = await crud_world.create_world(db, world_data, user_id)
        
        logger.info(f"Created world '{world_name}' (ID: {world.id}) from world builder for user {user_id}")
        
        return world
    
    async def update_world_from_builder(
        self,
        world_id: int,
        answers: Dict[int, int],
        generated_content: Dict[str, str],
        db: AsyncSession
    ) -> World:
        """
        Update an existing world with new world builder data
        
        Args:
            world_id: ID of the world to update
            answers: Dict mapping question_id to answer_id
            generated_content: Dict with AI-generated descriptions
            db: Database session
            
        Returns:
            Updated World object
        """
        # Get existing world
        world = await crud_world.get_world(db, world_id)
        if not world:
            raise ValueError(f"World {world_id} not found")
        
        # Prepare world builder data
        world_builder_data = {
            "answers": answers,
            "questions_version": "1.0",
            "updated_at": str(datetime.datetime.now(datetime.UTC))
        }
        
        # Update world data
        update_data = WorldUpdate(
            description=generated_content.get("description"),
            short_description=generated_content.get("short_description"),
            image_prompt_definition=generated_content.get("visual_prompt"),
            world_builder_data=world_builder_data
        )
        
        # Update the world
        world = await crud_world.update_world(db, world, update_data)
        
        logger.info(f"Updated world '{world.name}' (ID: {world.id}) from world builder")
        
        return world
    
    def get_answer_summary(self, answers: Dict[int, int]) -> List[Dict[str, str]]:
        """
        Get a human-readable summary of the selected answers
        
        Returns:
            List of dicts with 'question' and 'answer' keys
        """
        summary = []
        
        for question_id, answer_id in sorted(answers.items()):
            question = self.get_question_by_id(question_id)
            if not question:
                continue
            
            # Find the selected answer
            selected_answer = None
            for answer in question.get("answers", []):
                if answer["id"] == answer_id:
                    selected_answer = answer
                    break
            
            if selected_answer:
                summary.append({
                    "question": question["full_question"],
                    "answer": selected_answer["text"]
                })
        
        return summary


# Import datetime for timestamps
import datetime

# Global service instance
world_builder_service = WorldBuilderService()
