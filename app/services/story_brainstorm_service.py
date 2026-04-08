"""
Story Brainstorm Service

Handles the generation of story concepts and three-act structures using AI.
"""

import json
import uuid
import logging
import markdown
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.user_interview_response import UserInterviewResponse
from app.models.brainstorm_session import BrainstormSession, BrainstormFavorite, BrainstormStory
from app.models.story import Story
from app.models.world import World
from app.models.act import Act
from app.schemas.story import StoryCreate
from app.crud import story as story_crud
from app.services.langgraph_runtime_setup import generate_story_concepts_function, generate_three_act_structure_function, kernel
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result
from app.services.ai_model_cache import model_cache

logger = logging.getLogger(__name__)


class StoryBrainstormService:
    """Service for managing story brainstorm sessions and AI generation"""
    
    def __init__(self):
        # Functions are already registered in the shared storytelling runtime setup.
        pass
    
    async def generate_story_concepts(
        self, 
        user: User, 
        interview_response_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate 15 story concepts based on user's interview responses.
        
        Args:
            user: The user requesting story concepts
            interview_response_id: ID of the story_brainstorm interview response
            db: Database session
            
        Returns:
            Dictionary containing session info and generated concepts
        """
        try:
            # Get the interview response
            result = await db.execute(
                select(UserInterviewResponse).filter(
                    UserInterviewResponse.id == interview_response_id,
                    UserInterviewResponse.user_id == user.id,
                    UserInterviewResponse.interview_id == "story_brainstorm"
                )
            )
            interview_response = result.scalar_one_or_none()
            
            if not interview_response:
                raise ValueError("Interview response not found")
            
            # Extract and format interview data for AI
            formatted_data = self._format_interview_data(interview_response)
            
            logger.info(f"Generating story concepts for user {user.id} with data: {formatted_data}")
            
            # Generate concepts using the shared storytelling runtime.
            concepts_json = await self._call_ai_for_concepts(formatted_data, user, db)
            
            # Log the raw response for debugging
            logger.info(f"Raw AI response for concepts: {concepts_json[:500]}...")  # Log first 500 chars
            
            # Parse the JSON response
            try:
                # First try to parse as-is
                concepts = json.loads(concepts_json)
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code blocks
                logger.warning(f"Initial JSON parse failed, attempting to extract from markdown: {e}")
                
                # Look for JSON array pattern
                import re
                json_match = re.search(r'\[\s*\{.*?\}\s*\]', concepts_json, re.DOTALL)
                if json_match:
                    try:
                        concepts = json.loads(json_match.group(0))
                        logger.info("Successfully extracted JSON from response")
                    except json.JSONDecodeError as e2:
                        logger.error(f"Failed to parse extracted JSON: {e2}")
                        logger.error(f"Raw response: {concepts_json}")
                        raise ValueError(f"AI returned invalid JSON: {e2}")
                else:
                    logger.error(f"No JSON array found in response")
                    logger.error(f"Raw response: {concepts_json}")
                    raise ValueError(f"AI response does not contain a valid JSON array")
            
            # Add unique IDs to concepts if not present
            for i, concept in enumerate(concepts):
                if 'id' not in concept:
                    concept['id'] = f"concept-{uuid.uuid4().hex[:8]}"
            
            # Create brainstorm session
            session = BrainstormSession(
                user_id=user.id,
                interview_response_id=interview_response_id,
                session_name=f"Brainstorm Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            session.set_concepts(concepts)
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Created brainstorm session {session.id} with {len(concepts)} concepts")
            
            return {
                "session_id": session.id,
                "concepts": concepts,
                "concept_count": len(concepts),
                "created_at": session.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating story concepts: {e}")
            await db.rollback()
            raise
    
    async def save_favorite_concept(
        self,
        user: User,
        session_id: int,
        concept_id: str,
        db: AsyncSession
    ) -> BrainstormFavorite:
        """
        Save a story concept as a user's favorite.
        
        Args:
            user: The user saving the favorite
            session_id: ID of the brainstorm session
            concept_id: ID of the concept within the session
            db: Database session
            
        Returns:
            The created BrainstormFavorite object
        """
        try:
            # Get the session and verify ownership
            result = await db.execute(
                select(BrainstormSession).filter(
                    BrainstormSession.id == session_id,
                    BrainstormSession.user_id == user.id
                )
            )
            session = result.scalar_one_or_none()
            
            if not session:
                raise ValueError("Brainstorm session not found")
            
            # Get the specific concept
            concept_data = session.get_concept_by_id(concept_id)
            if not concept_data:
                raise ValueError("Concept not found in session")
            
            # Check if already favorited
            existing_result = await db.execute(
                select(BrainstormFavorite).filter(
                    BrainstormFavorite.user_id == user.id,
                    BrainstormFavorite.session_id == session_id,
                    BrainstormFavorite.concept_id == concept_id
                )
            )
            existing_favorite = existing_result.scalar_one_or_none()
            
            if existing_favorite:
                return existing_favorite
            
            # Create new favorite
            favorite = BrainstormFavorite(
                user_id=user.id,
                session_id=session_id,
                concept_id=concept_id
            )
            favorite.set_concept_data(concept_data)
            
            db.add(favorite)
            await db.commit()
            await db.refresh(favorite)
            
            logger.info(f"User {user.id} saved concept {concept_id} as favorite")
            
            return favorite
            
        except Exception as e:
            logger.error(f"Error saving favorite concept: {e}")
            await db.rollback()
            raise
    
    async def remove_favorite_concept(
        self,
        user: User,
        favorite_id: int,
        db: AsyncSession
    ) -> bool:
        """
        Remove a concept from user's favorites.
        
        Args:
            user: The user removing the favorite
            favorite_id: ID of the favorite to remove
            db: Database session
            
        Returns:
            True if removed successfully
        """
        try:
            # First, check if the favorite exists and belongs to the user
            result = await db.execute(
                select(BrainstormFavorite).filter(
                    BrainstormFavorite.id == favorite_id,
                    BrainstormFavorite.user_id == user.id
                )
            )
            favorite = result.scalar_one_or_none()
            
            if not favorite:
                raise ValueError("Favorite not found")
            
            # Check if there are any stories created from this favorite
            stories_result = await db.execute(
                select(BrainstormStory).filter(
                    BrainstormStory.favorite_id == favorite_id,
                    BrainstormStory.user_id == user.id
                )
            )
            dependent_stories = stories_result.scalars().all()
            
            if dependent_stories:
                # If there are stories created from this favorite, we should not delete it
                # Instead, provide a meaningful error message
                story_titles = [story.title for story in dependent_stories]
                raise ValueError(
                    f"Cannot delete this favorite concept because it was used to create "
                    f"{len(dependent_stories)} story(ies): {', '.join(story_titles)}. "
                    f"Delete the associated stories first if you want to remove this favorite."
                )
            
            # If no dependent stories, safe to delete the favorite
            await db.delete(favorite)
            await db.commit()
            
            logger.info(f"User {user.id} removed favorite {favorite_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing favorite concept: {e}")
            await db.rollback()
            raise
    
    async def generate_three_act_story(
        self,
        user: User,
        favorite_id: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate a three-act story structure from a favorite concept.
        
        Args:
            user: The user creating the story
            favorite_id: ID of the favorite concept
            db: Database session
            
        Returns:
            Dictionary containing the generated three-act structure
        """
        try:
            # Get the favorite concept
            favorite_result = await db.execute(
                select(BrainstormFavorite).filter(
                    BrainstormFavorite.id == favorite_id,
                    BrainstormFavorite.user_id == user.id
                )
            )
            favorite = favorite_result.scalar_one_or_none()
            
            if not favorite:
                raise ValueError("Favorite concept not found")
            
            # Get the original interview data
            session_result = await db.execute(
                select(BrainstormSession).filter(
                    BrainstormSession.id == favorite.session_id
                )
            )
            session = session_result.scalar_one_or_none()
            
            if not session:
                raise ValueError("Brainstorm session not found")
            
            interview_result = await db.execute(
                select(UserInterviewResponse).filter(
                    UserInterviewResponse.id == session.interview_response_id
                )
            )
            interview_response = interview_result.scalar_one_or_none()
            
            if not interview_response:
                raise ValueError("Interview response not found")
            
            # Format data for AI
            concept_data = favorite.get_concept_data()
            interview_data = self._format_interview_data(interview_response)
            
            logger.info(f"Generating three-act structure for concept: {concept_data.get('title')}")
            
            # Generate three-act structure using AI
            three_acts_json = await self._call_ai_for_three_acts(concept_data, interview_data, user, db)
            
            # Log the raw response for debugging
            logger.info(f"Raw AI response for three acts: {three_acts_json[:500]}...")  # Log first 500 chars
            
            # Parse the JSON response
            try:
                # First try to parse as-is
                three_acts = json.loads(three_acts_json)
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code blocks
                logger.warning(f"Initial JSON parse failed, attempting to extract from markdown: {e}")
                
                # Look for JSON object pattern (with or without scene suggestions)
                import re
                json_match = re.search(r'\{.*?"act1".*?"act2".*?"act3".*?\}', three_acts_json, re.DOTALL)
                if json_match:
                    try:
                        three_acts = json.loads(json_match.group(0))
                        logger.info("Successfully extracted JSON from response")
                    except json.JSONDecodeError as e2:
                        logger.error(f"Failed to parse extracted JSON: {e2}")
                        logger.error(f"Raw response: {three_acts_json}")
                        raise ValueError(f"AI returned invalid JSON: {e2}")
                else:
                    logger.error(f"No JSON object found in response")
                    logger.error(f"Raw response: {three_acts_json}")
                    raise ValueError(f"AI response does not contain a valid JSON object")
            
            # Create a shadow world for the story
            shadow_world = World(
                name=f"{concept_data.get('title', 'Untitled')} World",
                description=f"Auto-generated world for the story '{concept_data.get('title', 'Untitled Story')}'",
                short_description=f"World for {concept_data.get('title', 'Untitled Story')}",
                user_id=user.id,
                is_shadow=True,
                is_free_chat_enabled=False
            )
            
            db.add(shadow_world)
            await db.flush()
            await db.refresh(shadow_world)
            
            # Create the actual story
            story_create_data = StoryCreate(
                title=concept_data.get('title', 'Untitled Story'),
                short_description=concept_data.get('synopsis', ''),
                world_id=shadow_world.id,
                story_type='basic'
            )
            
            actual_story = await story_crud.create_story(
                db=db,
                story=story_create_data,
                user_id=user.id
            )
            
            # For basic stories, create a single act with all content combined
            # Format the three acts into a cohesive narrative with scene suggestions
            def format_scenes(scenes_list):
                if not scenes_list or not isinstance(scenes_list, list):
                    return ""
                return "\n".join([f"- {scene}" for scene in scenes_list])

            combined_content_markdown = f"""# {concept_data.get('title', 'Untitled Story')}

## Act 1: Setup

{three_acts.get('act1', '')}

### Scene Suggestions:
{format_scenes(three_acts.get('act1_scenes', []))}

## Act 2: Confrontation

{three_acts.get('act2', '')}

### Scene Suggestions:
{format_scenes(three_acts.get('act2_scenes', []))}

## Act 3: Resolution

{three_acts.get('act3', '')}

### Scene Suggestions:
{format_scenes(three_acts.get('act3_scenes', []))}
"""
            
            # Convert markdown to HTML for database storage
            combined_content_html = markdown.markdown(
                combined_content_markdown,
                extensions=['nl2br', 'fenced_code', 'tables']
            )
            
            logger.info(f"Converted markdown to HTML. Original length: {len(combined_content_markdown)}, HTML length: {len(combined_content_html)}")
            
            # Create a single act for the basic story
            single_act = Act(
                title="Complete Story",
                act_number=1,
                story_id=actual_story.id,
                description=combined_content_html
            )
            db.add(single_act)
            
            await db.flush()
            await db.refresh(single_act)
            
            created_acts = [single_act]
            
            # Create brainstorm story record for tracking
            story_record = BrainstormStory(
                user_id=user.id,
                favorite_id=favorite_id,
                title=concept_data.get('title', 'Untitled Story'),
                story_id=actual_story.id  # Link to the actual story
            )
            story_record.set_three_acts(three_acts)
            
            db.add(story_record)
            await db.commit()
            await db.refresh(story_record)
            await db.refresh(actual_story)
            
            logger.info(f"Created complete story {actual_story.id} with 3 acts for user {user.id}")
            
            return {
                "story_id": actual_story.id,
                "brainstorm_story_id": story_record.id,
                "title": story_record.title,
                "three_acts": three_acts,
                "concept": concept_data,
                "acts": [{"id": act.id, "title": act.title, "act_number": act.act_number} for act in created_acts]
            }
            
        except Exception as e:
            logger.error(f"Error generating three-act story: {e}")
            await db.rollback()
            raise
    
    def _format_interview_data(self, interview_response: UserInterviewResponse) -> Dict[str, Any]:
        """Format interview response data for AI consumption"""
        
        # Get the raw response data
        response_data = interview_response.get_response_data()
        responses = response_data.get('responses', {})
        
        # Extract story brainstorm specific data
        formatted_data = {
            'genres': [],
            'tone': [],
            'characters': {
                'character1': {
                    'role': [],
                    'name': '',
                    'background': ''
                },
                'character2': {
                    'role': [],
                    'name': '',
                    'background': ''
                }
            },
            'elements': []
        }
        
        # Extract genres
        genre_response = responses.get('genre_selection', {})
        formatted_data['genres'] = genre_response.get('selected_values', [])
        
        # Extract tone
        tone_response = responses.get('story_tone', {})
        formatted_data['tone'] = tone_response.get('selected_values', [])
        
        # Extract character 1 data
        char1_role = responses.get('character1_role', {})
        char1_name = responses.get('character1_name', {})
        char1_background = responses.get('character1_background', {})
        
        formatted_data['characters']['character1'] = {
            'role': char1_role.get('selected_values', []),
            'name': char1_name.get('text_value', ''),
            'background': char1_background.get('text_value', '')
        }
        
        # Extract character 2 data
        char2_role = responses.get('character2_role', {})
        char2_name = responses.get('character2_name', {})
        char2_background = responses.get('character2_background', {})
        
        formatted_data['characters']['character2'] = {
            'role': char2_role.get('selected_values', []),
            'name': char2_name.get('text_value', ''),
            'background': char2_background.get('text_value', '')
        }
        
        # Extract story elements
        elements_response = responses.get('story_elements', {})
        formatted_data['elements'] = elements_response.get('selected_values', [])
        
        return formatted_data
    
    async def _call_ai_for_concepts(self, interview_data: Dict[str, Any], user: User, db: AsyncSession) -> str:
        """Call AI to generate story concepts"""
        try:
            if not generate_story_concepts_function:
                raise RuntimeError("Story concepts generation function not available")
            
            # Extract data for the prompt template variables
            char1 = interview_data.get('characters', {}).get('character1', {})
            char2 = interview_data.get('characters', {}).get('character2', {})
            
            # Prepare arguments for the storytelling runtime function
            function_args = {
                "genres": ", ".join(interview_data.get('genres', [])),
                "tone": ", ".join(interview_data.get('tone', [])),
                "elements": ", ".join(interview_data.get('elements', [])),
                "char1_role": ", ".join(char1.get('role', [])),
                "char1_name": char1.get('name', ''),
                "char1_background": char1.get('background', ''),
                "char2_role": ", ".join(char2.get('role', [])),
                "char2_name": char2.get('name', ''),
                "char2_background": char2.get('background', '')
            }
            
            logger.info(f"Calling AI for story concepts with args: {function_args}")
            
            # Invoke the function with the kernel and formatted arguments
            result = await generate_story_concepts_function.invoke(kernel, **function_args)
            
            # Log AI cost tracking
            logger.info(f"About to log AI cost for story concepts generation")
            logger.info(f"SK result type: {type(result)}")
            logger.info(f"SK result value: {str(result)[:200]}...")
            await self._log_ai_cost(
                result=result,
                call_type="story_brainstorm_concepts", 
                input_data=function_args,
                user=user,
                db=db
            )
            logger.info(f"Completed logging AI cost for story concepts generation")
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error calling AI for concepts: {e}")
            raise
    
    async def _call_ai_for_three_acts(self, concept_data: Dict[str, Any], interview_data: Dict[str, Any], user: User, db: AsyncSession) -> str:
        """Call AI to generate three-act structure"""
        try:
            if not generate_three_act_structure_function:
                raise RuntimeError("Three-act structure generation function not available")
            
            # Extract data for the prompt template variables
            char1 = interview_data.get('characters', {}).get('character1', {})
            char2 = interview_data.get('characters', {}).get('character2', {})
            
            # Prepare arguments for the storytelling runtime function
            function_args = {
                "title": concept_data.get('title', ''),
                "synopsis": concept_data.get('synopsis', ''),
                "genres": ", ".join(interview_data.get('genres', [])),
                "tone": ", ".join(interview_data.get('tone', [])),
                "elements": ", ".join(interview_data.get('elements', [])),
                "char1_role": ", ".join(char1.get('role', [])),
                "char1_name": char1.get('name', ''),
                "char1_background": char1.get('background', ''),
                "char2_role": ", ".join(char2.get('role', [])),
                "char2_name": char2.get('name', ''),
                "char2_background": char2.get('background', '')
            }
            
            logger.info(f"Calling AI for three-act structure with concept: {concept_data.get('title')}")
            
            # Invoke the function with the kernel and formatted arguments
            result = await generate_three_act_structure_function.invoke(kernel, **function_args)
            
            # Log AI cost tracking
            await self._log_ai_cost(
                result=result,
                call_type="story_brainstorm_three_acts",
                input_data=function_args,
                user=user,
                db=db
            )
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error calling AI for three acts: {e}")
            raise
    
    async def _log_ai_cost(
        self, 
        result, 
        call_type: str, 
        input_data: Dict[str, Any], 
        user: User,
        db: AsyncSession
    ) -> None:
        """Log AI cost for story brainstorm operations"""
        try:
            logger.info(f"Starting _log_ai_cost for {call_type}")
            
            # Get the default generation model configuration
            model_config = model_cache.default_generation_model
            logger.info(f"Model config: {model_config.model_name if model_config else 'None'}")
            
            if not model_config:
                logger.warning("No model configuration found for cost tracking")
                return
            
            # Extract usage data from the storytelling runtime result
            logger.info(f"Extracting usage data from SK result for {call_type}")
            usage_data = get_usage_from_sk_result(result)
            logger.info(f"Extracted usage data: {usage_data}")
            
            # If no usage data found or zero values, estimate it manually
            if not usage_data or usage_data.get("total_tokens", 0) == 0:
                logger.warning(f"No valid usage data found in SK result (provider: {model_config.provider}), estimating token usage manually for {call_type}")
                from app.services.cost_tracker_service import estimate_tokens_for_streaming_call
                
                # Estimate tokens for input (function args) and output (result)
                input_text = f"Story Brainstorm - {call_type}: " + str(input_data)
                output_text = str(result)
                
                usage_data = estimate_tokens_for_streaming_call(
                    input_text=input_text,
                    output_text=output_text,
                    model_name=model_config.model_name
                )
                logger.info(f"Estimated token usage for {model_config.provider} provider on {call_type}: {usage_data}")
            else:
                logger.info(f"Using actual usage data from {model_config.provider} provider for {call_type}: {usage_data}")
            
            # Create input prompt from function args for logging
            input_prompt = f"Story Brainstorm - {call_type}: " + str(input_data)
            logger.info(f"Input prompt length: {len(input_prompt)}")
            
            # Ensure we have valid usage data before logging
            if usage_data and usage_data.get("total_tokens", 0) > 0:
                # Log the AI call with cost tracking
                logger.info(f"Calling log_ai_call for {call_type}")
                await log_ai_call(
                    user_id=user.id,
                    model_config=model_config,
                    input_prompt=input_prompt,
                    usage=usage_data,
                    call_type=call_type,
                    db=db
                )
                
                logger.info(f"Successfully logged AI cost for {call_type}: {usage_data.get('total_tokens', 0)} tokens")
            else:
                logger.error(f"Failed to get valid token usage data for {call_type}, skipping cost logging")
            
        except Exception as e:
            logger.error(f"Failed to log AI cost for {call_type}: {e}", exc_info=True)
            # Don't raise - cost logging failure shouldn't break the main flow
