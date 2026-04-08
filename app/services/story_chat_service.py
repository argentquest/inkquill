"""Service helpers for story chat service."""

# /story_app/app/services/story_chat_service.py

import logging
from typing import List, Optional, Dict, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc, func

from app.models.story import Story
from app.models.act import Act
from app.models.story_chat_session import StoryChatSession
from app.models.story_chat_message import StoryChatMessage
from app.models.user import User
from app.schemas.story_chat import (
    StoryChatSessionCreate, StoryChatSessionRead, StoryChatSessionWithMessages,
    StoryChatMessageCreate, StoryChatMessageRead, SendStoryChatMessageRequest,
    StoryContextSummary
)
from app.services.cost_tracker_service import CostTrackerService
from app.services.ai_model_cache import model_cache
from app.services import storytelling_runtime

logger = logging.getLogger(__name__)

class StoryChatService:
    """
    Service for managing story chat sessions and AI conversations about stories.
    
    This service handles:
    - Creating and managing story chat sessions
    - Processing chat messages with AI integration
    - Loading story context for conversations
    - Cost tracking for AI interactions
    - Supporting both Basic and Advanced story types
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cost_tracker = CostTrackerService(db)
    
    # --- Session Management ---
    
    async def create_session(
        self, 
        story_id: int, 
        user_id: int, 
        session_data: StoryChatSessionCreate
    ) -> StoryChatSessionRead:
        """Create a new story chat session"""
        
        # Verify story exists and user has access
        story = await self._get_story_with_access_check(story_id, user_id)
        
        # Create session
        session = StoryChatSession(
            story_id=story_id,
            user_id=user_id,
            title=session_data.title,
            description=session_data.description,
            focus_area=session_data.focus_area or 'general'
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(f"Created story chat session {session.id} for story {story_id}")
        return StoryChatSessionRead.model_validate(session)
    
    async def get_sessions(self, story_id: int, user_id: int) -> List[StoryChatSessionRead]:
        """Get all chat sessions for a story"""
        
        # Verify access
        await self._get_story_with_access_check(story_id, user_id)
        
        result = await self.db.execute(
            select(StoryChatSession)
            .where(StoryChatSession.story_id == story_id)
            .where(StoryChatSession.user_id == user_id)
            .order_by(desc(StoryChatSession.updated_at))
        )
        sessions = result.scalars().all()
        
        return [StoryChatSessionRead.model_validate(session) for session in sessions]
    
    async def get_session_with_messages(
        self, 
        story_id: int, 
        session_id: int, 
        user_id: int
    ) -> Optional[StoryChatSessionWithMessages]:
        """Get a chat session with all its messages"""
        
        # Verify access
        await self._get_story_with_access_check(story_id, user_id)
        
        result = await self.db.execute(
            select(StoryChatSession)
            .options(selectinload(StoryChatSession.messages))
            .where(StoryChatSession.id == session_id)
            .where(StoryChatSession.story_id == story_id)
            .where(StoryChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return None
            
        return StoryChatSessionWithMessages.model_validate(session)
    
    async def delete_session(self, story_id: int, session_id: int, user_id: int) -> bool:
        """Delete a chat session"""
        
        # Verify access
        await self._get_story_with_access_check(story_id, user_id)
        
        result = await self.db.execute(
            select(StoryChatSession)
            .where(StoryChatSession.id == session_id)
            .where(StoryChatSession.story_id == story_id)
            .where(StoryChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
            
        await self.db.delete(session)
        await self.db.commit()
        
        logger.info(f"Deleted story chat session {session_id}")
        return True
    
    # --- Message Processing ---
    
    async def send_message(
        self, 
        story_id: int, 
        session_id: int, 
        user_id: int, 
        request: SendStoryChatMessageRequest
    ) -> AsyncGenerator[str, None]:
        """
        Send a message and get AI response (streaming)
        """
        
        # Verify access and get session
        session = await self._get_session_with_access_check(story_id, session_id, user_id)
        story = await self._load_story_context(story_id)
        
        # Save user message
        user_message = StoryChatMessage(
            session_id=session_id,
            role='user',
            content=request.message,
            target_element=request.target_element,
            target_element_id=request.target_element_id
        )
        self.db.add(user_message)
        await self.db.commit()
        
        # Prepare context for AI
        context = await self._build_ai_context(story, session, request)
        
        # Get AI response
        ai_response = ""
        cost_log_id = None
        
        try:
            # Get AI model configuration
            ai_config = model_cache.default_generation_model
            if not ai_config:
                raise ValueError("No default AI model configuration available")
            kernel = storytelling_runtime.kernel
            
            # Prepare messages for AI
            messages = await self._prepare_chat_messages(session_id, context)
            
            # Start cost tracking
            cost_log = await self.cost_tracker.start_ai_call(
                user_id=user_id,
                operation_type='story_chat',
                model_name=ai_config.model_name,
                context={'story_id': story_id, 'session_id': session_id}
            )
            cost_log_id = cost_log.id
            
            # Stream AI response
            async for chunk in self._stream_ai_response(kernel, messages, ai_config):
                ai_response += chunk
                yield chunk
                
        except Exception as e:
            logger.error(f"Error in AI response: {e}")
            error_msg = "I'm sorry, I encountered an error processing your message. Please try again."
            ai_response = error_msg
            yield error_msg
        
        # Save AI response
        ai_message = StoryChatMessage(
            session_id=session_id,
            role='assistant',
            content=ai_response,
            full_context=context,
            story_context=await self._get_story_context_summary(story),
            cost_log_id=cost_log_id
        )
        self.db.add(ai_message)
        
        # Update session timestamp
        session.updated_at = func.now()
        
        await self.db.commit()
        
        # Finalize cost tracking
        if cost_log_id:
            await self.cost_tracker.finish_ai_call(
                cost_log_id, 
                ai_response, 
                success=True
            )
    
    # --- Context Building ---
    
    async def _load_story_context(self, story_id: int) -> Story:
        """Load complete story context"""
        result = await self.db.execute(
            select(Story)
            .options(
                selectinload(Story.acts).selectinload(Act.scenes),
                selectinload(Story.world),
                selectinload(Story.characters),
                selectinload(Story.locations),
                selectinload(Story.lore_items)
            )
            .where(Story.id == story_id)
        )
        return result.scalar_one()
    
    async def _build_ai_context(
        self, 
        story: Story, 
        session: StoryChatSession, 
        request: SendStoryChatMessageRequest
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI conversation"""
        
        context = {
            'story': {
                'id': story.id,
                'title': story.title,
                'description': story.short_description,
                'type': story.story_type,
                'genre': story.story_genre,
                'tone': story.story_tone
            },
            'session': {
                'focus_area': session.focus_area,
                'title': session.title
            },
            'request': {
                'target_element': request.target_element,
                'target_element_id': request.target_element_id
            }
        }
        
        # Add story structure with FULL CONTENT for better AI context
        context['acts'] = []
        target_act_id = request.target_element_id if request.target_element == 'act' else None
        target_scene_id = request.target_element_id if request.target_element == 'scene' else None
        
        for act in sorted(story.acts, key=lambda a: a.act_number):
            act_data = {
                'id': act.id,
                'title': act.title,
                'act_number': act.act_number,
                'scenes': []
            }
            
            # Include FULL CONTENT for current target act and all previous acts
            if target_act_id and act.id == target_act_id:
                # This is the target act - include full content
                act_data['content'] = act.content or ""
                act_data['is_target'] = True
            elif target_act_id and act.act_number < next(
                (a.act_number for a in story.acts if a.id == target_act_id), float('inf')
            ):
                # This is a previous act - include full content for context
                act_data['content'] = act.content or ""
                act_data['is_previous'] = True
            else:
                # For non-target acts, include preview or full content if small
                content = act.content or ""
                if len(content) <= 1000:
                    act_data['content'] = content
                else:
                    act_data['content_preview'] = content[:500] + "..."
            
            # Handle scenes with full content logic
            for scene in sorted(act.scenes, key=lambda s: s.scene_number):
                scene_data = {
                    'id': scene.id,
                    'title': scene.title,
                    'scene_number': scene.scene_number,
                }
                
                # Include FULL CONTENT for target scene and all previous scenes in current/previous acts
                if target_scene_id and scene.id == target_scene_id:
                    # This is the target scene - include full content
                    scene_data['content'] = scene.content or ""
                    scene_data['is_target'] = True
                elif target_scene_id:
                    # For scene targeting, include all previous scenes in chronological order
                    target_scene = next((s for a in story.acts for s in a.scenes if s.id == target_scene_id), None)
                    if target_scene and self._is_scene_before_target(scene, target_scene, story.acts):
                        scene_data['content'] = scene.content or ""
                        scene_data['is_previous'] = True
                    else:
                        content = scene.content or ""
                        scene_data['content_preview'] = content[:300] + "..." if len(content) > 300 else content
                elif target_act_id and act.id == target_act_id:
                    # If targeting an act, include all scenes in that act
                    scene_data['content'] = scene.content or ""
                elif target_act_id and act.act_number < next(
                    (a.act_number for a in story.acts if a.id == target_act_id), float('inf')
                ):
                    # Previous act scenes - include full content
                    scene_data['content'] = scene.content or ""
                else:
                    # Default: preview or full if small
                    content = scene.content or ""
                    if len(content) <= 500:
                        scene_data['content'] = content
                    else:
                        scene_data['content_preview'] = content[:300] + "..."
                
                act_data['scenes'].append(scene_data)
            
            context['acts'].append(act_data)
        
        # DIFFERENT CONTEXT BASED ON STORY TYPE
        if story.story_type == 'basic':
            # Basic stories: Focus only on the story content itself
            # No world-building elements, no character sheets, no locations
            context['world_context'] = None
            context['characters'] = []
            context['locations'] = []
            context['lore_items'] = []
            context['is_basic_story'] = True
            
            # Add note that this is a Basic story focused on writing
            context['story_focus'] = "basic_writing_focused"
            
        elif story.story_type == 'advanced':
            # Advanced stories: Include full world context
            context['is_basic_story'] = False
            context['story_focus'] = "advanced_world_building"
            
            if story.world and not getattr(story.world, 'is_shadow', False):
                context['world'] = {
                    'name': story.world.name,
                    'description': story.world.description
                }
                
                # Add characters, locations, lore
                context['characters'] = [
                    {'id': c.id, 'name': c.name, 'description': c.description[:200]}
                    for c in story.characters[:10]  # Limit to avoid token overflow
                ]
                
                context['locations'] = [
                    {'id': l.id, 'name': l.name, 'description': l.description[:200]}
                    for l in story.locations[:10]
                ]
                
                context['lore_items'] = [
                    {'id': li.id, 'name': li.name, 'description': li.description[:200]}
                    for li in story.lore_items[:5]
                ]
            else:
                # Advanced story but no real world data yet
                context['world'] = None
                context['characters'] = []
                context['locations'] = []
                context['lore_items'] = []
        
        return context
    
    async def _prepare_chat_messages(self, session_id: int, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare message history for AI"""
        
        # Get recent messages from session
        result = await self.db.execute(
            select(StoryChatMessage)
            .where(StoryChatMessage.session_id == session_id)
            .order_by(StoryChatMessage.created_at)
            .limit(20)  # Last 20 messages for context
        )
        messages = result.scalars().all()
        
        # Build system prompt based on story type and context
        system_prompt = self._build_system_prompt(context)
        
        ai_messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in messages:
            ai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return ai_messages
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt for story chat AI using appropriate template"""
        
        from jinja2 import Template
        
        story = context['story']
        
        # Load appropriate prompt template based on story type
        if story['type'] == 'basic':
            from app.prompts.story_chat.basic_story_chat import BASIC_STORY_CHAT_PROMPT
            template_str = BASIC_STORY_CHAT_PROMPT
        else:
            from app.prompts.story_chat.advanced_story_chat import ADVANCED_STORY_CHAT_PROMPT
            template_str = ADVANCED_STORY_CHAT_PROMPT
        
        # Prepare template variables
        template_vars = {
            'story_title': story['title'],
            'story_description': story.get('description', 'No description provided'),
            'story_genre': story.get('genre'),
            'story_tone': story.get('tone'),
            'session_focus': context['session'].get('focus_area'),
            'acts': context.get('acts', []),
            'world': context.get('world'),
            'characters': context.get('characters', []),
            'locations': context.get('locations', []),
            'lore_items': context.get('lore_items', []),
            'target_element': context['request'].get('target_element'),
            'target_element_id': context['request'].get('target_element_id')
        }
        
        # Render template
        template = Template(template_str)
        return template.render(**template_vars)
    
    async def _stream_ai_response(self, kernel, messages, ai_config) -> AsyncGenerator[str, None]:
        """Stream AI response chunks"""
        
        # Get the story chat function from kernel
        story_chat_function = kernel.get_function("storytelling", "story_discussion")
        
        # Prepare the prompt with conversation context
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages[-5:]  # Last 5 messages
        ])
        
        # Stream the response
        response = story_chat_function.invoke(
            conversation=conversation_text
        )
        
        # For now, yield the complete response
        # In future, implement actual streaming
        yield str(response)
    
    # --- Helper Methods ---
    
    async def _get_story_with_access_check(self, story_id: int, user_id: int) -> Story:
        """Get story and verify user has access"""
        result = await self.db.execute(
            select(Story)
            .where(Story.id == story_id)
            .where(Story.user_id == user_id)
        )
        story = result.scalar_one_or_none()
        
        if not story:
            raise ValueError("Story not found or access denied")
            
        return story
    
    async def _get_session_with_access_check(
        self, 
        story_id: int, 
        session_id: int, 
        user_id: int
    ) -> StoryChatSession:
        """Get session and verify access"""
        result = await self.db.execute(
            select(StoryChatSession)
            .where(StoryChatSession.id == session_id)
            .where(StoryChatSession.story_id == story_id)
            .where(StoryChatSession.user_id == user_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError("Session not found or access denied")
            
        return session
    
    def _is_scene_before_target(self, scene, target_scene, acts) -> bool:
        """Check if a scene comes before the target scene chronologically"""
        scene_act = next((a for a in acts if any(s.id == scene.id for s in a.scenes)), None)
        target_act = next((a for a in acts if any(s.id == target_scene.id for s in a.scenes)), None)
        
        if not scene_act or not target_act:
            return False
            
        # If in different acts, compare act numbers
        if scene_act.act_number != target_act.act_number:
            return scene_act.act_number < target_act.act_number
            
        # If in same act, compare scene numbers
        return scene.scene_number < target_scene.scene_number
    
    async def _get_story_context_summary(self, story: Story) -> Dict[str, Any]:
        """Get summary of story context for storage"""
        return {
            'story_id': story.id,
            'story_title': story.title,
            'story_type': story.story_type,
            'acts_count': len(story.acts) if story.acts else 0,
            'world_name': story.world.name if story.world else None
        }
