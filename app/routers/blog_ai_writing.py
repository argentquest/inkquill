"""Blog AI-assisted writing WebSocket endpoint."""

from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
)
from fastapi.websockets import WebSocketState 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json 
import time
import semantic_kernel as sk
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.function_result import FunctionResult 
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from typing import Dict, Any, Optional, List
import logging

from app.core.deps import get_db_session 
from app.models.user import User 
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_category import BlogCategory
from app.models.blog_tag import BlogTag
from app.crud import user as crud_user
from app.core.deps_ws import get_current_user_from_ws_ticket
from app.core.config import settings
from app.services.ai_model_cache import model_cache
from app.services.sk_kernel_instance import (
    kernel,
    generate_act_narrative_only_function,
    generate_scene_narrative_only_function
)
from app.services.sk_constants import (
    STORYTELLING_PLUGIN_NAME,
    STORY_ANALYSIS_PLUGIN_NAME
)
from app.services.cost_tracker_service import log_ai_streaming_call
from app.services.blog_prompt_service import BlogPromptService
from app.services.direct_context import build_document_context

logger = logging.getLogger(__name__)

router = APIRouter()

# Test endpoint to verify router is loaded
@router.get("/test-blog-ai")
async def test_blog_ai_endpoint():
    """Test endpoint to verify blog AI router is working."""
    return {"message": "Blog AI router is working", "status": "ok"}

# Test WebSocket endpoint (simplified)
@router.websocket("/test-ws/{session_id}")
async def test_websocket_endpoint(websocket: WebSocket, session_id: str):
    """Simple test WebSocket endpoint."""
    logger.info(f"TEST WEBSOCKET ENDPOINT REACHED: {session_id}")
    await websocket.accept()
    await websocket.send_text(f"Test WebSocket connected: {session_id}")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except:
        pass

class BlogWritingContextManager:
    """Context manager for blog writing sessions."""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, session_id: str):
        """Connect a user to the blog writing session."""
        # WebSocket is already accepted in the endpoint, just register it
        self.connections[session_id] = websocket
        self.user_sessions[session_id] = {
            "user_id": user_id,
            "connected_at": time.time()
        }
        logger.info(f"Blog writing session connected: user_id={user_id}, session_id={session_id}")
    
    def disconnect(self, session_id: str):
        """Disconnect a session."""
        if session_id in self.connections:
            del self.connections[session_id]
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
        logger.info(f"Blog writing session disconnected: session_id={session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send a message to a specific session."""
        if session_id in self.connections:
            websocket = self.connections[session_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
            else:
                self.disconnect(session_id)

blog_writing_manager = BlogWritingContextManager()


def extract_text_from_result(result) -> str:
    """Extract clean text content from Semantic Kernel result."""
    if not result or not result.value:
        return ""
    
    # If it's a list of ChatMessageContent objects
    if hasattr(result.value, '__iter__'):
        for item in result.value:
            if hasattr(item, 'text'):
                return item.text
            elif hasattr(item, 'content'):
                return item.content
    
    # If it's a single value, convert to string
    return str(result.value)


@router.websocket("/ws/blog-ai/{session_id}")
async def blog_ai_writing_endpoint(
    websocket: WebSocket,
    session_id: str
):
    """WebSocket endpoint for AI-assisted blog writing."""
    
    logger.info(f"=== BLOG AI WEBSOCKET ENDPOINT REACHED ===")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"Query params: {dict(websocket.query_params)}")
    
    try:
        # Accept the connection first
        await websocket.accept()
        logger.info(f"WebSocket accepted for session {session_id}")
        
        # Manual authentication
        ticket = websocket.query_params.get("ticket")
        if not ticket:
            await websocket.send_text(json.dumps({"type": "error", "message": "Authentication required"}))
            await websocket.close(code=1008, reason="No ticket")
            return
        
        # Get user manually without dependency
        from app.db.database import async_session_local
        from app.core import security
        from app.crud import user as crud_user
        
        async with async_session_local() as db:
            try:
                # Decode token
                payload = await security.decode_access_token(token=ticket)
                if not payload or payload.get("type") != "websocket":
                    raise ValueError("Invalid ticket")
                
                username = payload.get("sub")
                if not username:
                    raise ValueError("No username in ticket")
                
                # Get user
                current_user = await crud_user.get_user_by_username(db, username=username)
                if not current_user or not current_user.is_active:
                    raise ValueError("User not found or inactive")
                
                logger.info(f"Authenticated user: {current_user.username} (ID: {current_user.id})")
                
                # Connect to the blog writing manager
                await blog_writing_manager.connect(websocket, current_user.id, session_id)
                
                # Now handle the WebSocket connection
                await websocket.send_text(json.dumps({
                    "type": "connected",
                    "message": "Blog AI assistant ready",
                    "user": {
                        "id": current_user.id,
                        "username": current_user.username,
                        "display_name": current_user.display_name
                    }
                }))
                
                # Message handling loop
                while True:
                    try:
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        
                        # Use a new DB session for message handling
                        async with async_session_local() as msg_db:
                            await handle_blog_writing_message(session_id, message, current_user, msg_db)
                        
                    except WebSocketDisconnect:
                        logger.info(f"Blog writing WebSocket disconnected for session {session_id}")
                        blog_writing_manager.disconnect(session_id)
                        break
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from blog writing client {session_id}: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Invalid JSON format"
                        }))
                    except Exception as e:
                        logger.error(f"Error in blog writing session {session_id}: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error", 
                            "message": "Internal server error"
                        }))
                
            except Exception as auth_error:
                logger.error(f"Authentication failed: {auth_error}")
                await websocket.send_text(json.dumps({"type": "error", "message": "Authentication failed"}))
                await websocket.close(code=1008, reason="Authentication failed")
                return
    
    except Exception as e:
        logger.error(f"Error setting up blog writing WebSocket for session {session_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Server error")
        except:
            pass
    finally:
        # Always disconnect from manager
        blog_writing_manager.disconnect(session_id)


async def handle_blog_writing_message(
    session_id: str,
    message: Dict[str, Any],
    current_user: User,
    db: AsyncSession
):
    """Handle incoming blog writing messages."""
    
    message_type = message.get("type")
    
    if message_type == "generate_content":
        await handle_generate_content(session_id, message, current_user, db)
    elif message_type == "improve_writing":
        await handle_improve_writing(session_id, message, current_user, db)
    elif message_type == "generate_title":
        await handle_generate_title(session_id, message, current_user, db)
    elif message_type == "generate_excerpt":
        await handle_generate_excerpt(session_id, message, current_user, db)
    elif message_type == "suggest_tags":
        await handle_suggest_tags(session_id, message, current_user, db)
    elif message_type == "get_writing_tips":
        await handle_get_writing_tips(session_id, message, current_user, db)
    else:
        await blog_writing_manager.send_message(session_id, {
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })


async def handle_generate_content(
    session_id: str,
    message: Dict[str, Any],
    current_user: User,
    db: AsyncSession
):
    """Generate blog content based on topic and style."""
    
    try:
        topic = message.get("topic", "")
        style = message.get("style", "informative")
        category = message.get("category", "")
        length = message.get("length", "medium")
        existing_content = message.get("existing_content", "")
        
        if not topic:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Topic is required"
            })
            return
        
        # Get AI model settings
        model_settings = model_cache.default_generation_model
        if not model_settings:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "No AI models configured"
            })
            return
        
        # Build context
        context_parts = []
        
        # Add uploaded-document context if requested
        if message.get("use_world_context") and message.get("world_id"):
            try:
                document_context, _ = await build_document_context(
                    db,
                    int(message.get("world_id")),
                    topic,
                    max_documents=3,
                    max_chars_per_document=1200,
                )
                if document_context:
                    context_parts.append(f"World Context:\n{document_context}")
            except Exception as e:
                logger.warning(f"Failed to prepare uploaded-document context: {e}")
        
        # Generate prompt using prompt service
        prompt = BlogPromptService.format_content_generation_prompt(
            topic=topic,
            style=style,
            length=length,
            category=category,
            existing_content=existing_content,
            context_parts=context_parts
        )
        
        if not prompt:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to load content generation prompt"
            })
            return
        
        # Send "thinking" message
        await blog_writing_manager.send_message(session_id, {
            "type": "thinking",
            "message": f"Generating {length} blog content about {topic}..."
        })
        
        # Generate content
        execution_settings = OpenAIChatPromptExecutionSettings(
            max_tokens=model_settings.max_tokens,
            temperature=model_settings.temperature,
            top_p=model_settings.top_p
        )
        
        # Use existing function or plugin
        storytelling_plugin = kernel.plugins.get(STORYTELLING_PLUGIN_NAME)
        if storytelling_plugin and "GenerateContent" in storytelling_plugin:
            result: FunctionResult = await storytelling_plugin["GenerateContent"].invoke(
                kernel,
                KernelArguments(
                    prompt=prompt,
                    execution_settings=execution_settings
                )
            )
        else:
            # Fallback to narrative generation function
            result: FunctionResult = await generate_act_narrative_only_function.invoke(
                kernel,
                KernelArguments(
                    user_instruction=prompt,
                    execution_settings=execution_settings
                )
            )
        
        if result.value:
            # Extract clean text content from the result
            content_text = extract_text_from_result(result)
            
            # Track cost
            await log_ai_streaming_call(
                user_id=current_user.id,
                model_config=model_settings,
                input_prompt=prompt,
                output_text=content_text,
                call_type="blog_content_generation",
                db=db
            )
            
            await blog_writing_manager.send_message(session_id, {
                "type": "content_generated",
                "content": content_text,
                "topic": topic,
                "style": style,
                "length": length
            })
        else:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to generate content"
            })
    
    except Exception as e:
        logger.error(f"Error generating blog content: {e}")
        await blog_writing_manager.send_message(session_id, {
            "type": "error",
            "message": "Failed to generate content"
        })


async def handle_improve_writing(
    session_id: str,
    message: Dict[str, Any],
    current_user: User,
    db: AsyncSession
):
    """Improve existing blog content."""
    
    try:
        content = message.get("content", "")
        improvement_type = message.get("improvement_type", "general")
        
        if not content:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Content is required"
            })
            return
        
        # Get AI model settings
        model_settings = model_cache.default_generation_model
        if not model_settings:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "No AI models configured"
            })
            return
        
        # Generate prompt using prompt service
        prompt = BlogPromptService.format_improve_writing_prompt(
            content=content,
            improvement_type=improvement_type
        )
        
        if not prompt:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to load improvement prompt"
            })
            return
        
        # Send "thinking" message
        await blog_writing_manager.send_message(session_id, {
            "type": "thinking",
            "message": f"Improving content for {improvement_type}..."
        })
        
        # Improve content
        execution_settings = OpenAIChatPromptExecutionSettings(
            max_tokens=model_settings.max_tokens,
            temperature=0.3,  # Lower temperature for improvements
            top_p=model_settings.top_p
        )
        
        storytelling_plugin = kernel.plugins.get(STORYTELLING_PLUGIN_NAME)
        if storytelling_plugin and "ImproveContent" in storytelling_plugin:
            result: FunctionResult = await storytelling_plugin["ImproveContent"].invoke(
                kernel,
                KernelArguments(
                    prompt=prompt,
                    execution_settings=execution_settings
                )
            )
        else:
            # Fallback to narrative generation function
            result: FunctionResult = await generate_act_narrative_only_function.invoke(
                kernel,
                KernelArguments(
                    user_instruction=prompt,
                    execution_settings=execution_settings
                )
            )
        
        if result.value:
            # Extract clean text content from the result
            improved_text = extract_text_from_result(result)
            
            # Track cost
            await log_ai_streaming_call(
                user_id=current_user.id,
                model_config=model_settings,
                input_prompt=prompt,
                output_text=improved_text,
                call_type="blog_improvement",
                db=db
            )
            
            await blog_writing_manager.send_message(session_id, {
                "type": "content_improved",
                "original_content": content,
                "improved_content": improved_text,
                "improvement_type": improvement_type
            })
        else:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to improve content"
            })
    
    except Exception as e:
        logger.error(f"Error improving blog content: {e}")
        await blog_writing_manager.send_message(session_id, {
            "type": "error",
            "message": "Failed to improve content"
        })


async def handle_generate_title(
    session_id: str,
    message: Dict[str, Any],
    current_user: User,
    db: AsyncSession
):
    """Generate blog title suggestions."""
    
    try:
        content = message.get("content", "")
        topic = message.get("topic", "")
        style = message.get("style", "engaging")
        
        if not content and not topic:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Content or topic is required"
            })
            return
        
        # Get AI model settings
        model_settings = model_cache.default_generation_model
        if not model_settings:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "No AI models configured"
            })
            return
        
        # Generate prompt using prompt service
        prompt = BlogPromptService.format_generate_title_prompt(
            content=content,
            topic=topic,
            style=style
        )
        
        if not prompt:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to load title generation prompt"
            })
            return
        
        # Send "thinking" message
        await blog_writing_manager.send_message(session_id, {
            "type": "thinking",
            "message": "Generating title suggestions..."
        })
        
        # Generate titles
        execution_settings = OpenAIChatPromptExecutionSettings(
            max_tokens=200,
            temperature=0.8,  # Higher creativity for titles
            top_p=model_settings.top_p
        )
        
        storytelling_plugin = kernel.plugins.get(STORYTELLING_PLUGIN_NAME)
        if storytelling_plugin and "GenerateContent" in storytelling_plugin:
            result: FunctionResult = await storytelling_plugin["GenerateContent"].invoke(
                kernel,
                KernelArguments(
                    prompt=prompt,
                    execution_settings=execution_settings
                )
            )
        else:
            # Fallback to narrative generation function
            result: FunctionResult = await generate_act_narrative_only_function.invoke(
                kernel,
                KernelArguments(
                    user_instruction=prompt,
                    execution_settings=execution_settings
                )
            )
        
        if result.value:
            # Extract clean text content from the result
            titles_text = extract_text_from_result(result)
            
            # Track cost
            await log_ai_streaming_call(
                user_id=current_user.id,
                model_config=model_settings,
                input_prompt=prompt,
                output_text=titles_text,
                call_type="blog_title_generation",
                db=db
            )
            
            # Parse titles from response
            titles = []
            for line in titles_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove number/bullet and clean up
                    title = line.split('.', 1)[-1].split('-', 1)[-1].strip()
                    if title:
                        titles.append(title)
            
            await blog_writing_manager.send_message(session_id, {
                "type": "titles_generated",
                "titles": titles,
                "style": style
            })
        else:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to generate titles"
            })
    
    except Exception as e:
        logger.error(f"Error generating blog titles: {e}")
        await blog_writing_manager.send_message(session_id, {
            "type": "error",
            "message": "Failed to generate titles"
        })


async def handle_generate_excerpt(
    session_id: str,
    message: Dict[str, Any],
    current_user: User,
    db: AsyncSession
):
    """Generate blog excerpt from content."""
    
    try:
        content = message.get("content", "")
        
        if not content:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Content is required"
            })
            return
        
        # Get AI model settings
        model_settings = model_cache.default_generation_model
        if not model_settings:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "No AI models configured"
            })
            return
        
        # Generate prompt using prompt service
        prompt = BlogPromptService.format_generate_excerpt_prompt(content, max_length=200)
        
        if not prompt:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to load excerpt generation prompt"
            })
            return
        
        # Send "thinking" message
        await blog_writing_manager.send_message(session_id, {
            "type": "thinking",
            "message": "Generating excerpt..."
        })
        
        # Generate excerpt
        execution_settings = OpenAIChatPromptExecutionSettings(
            max_tokens=100,
            temperature=0.7,
            top_p=model_settings.top_p
        )
        
        storytelling_plugin = kernel.plugins.get(STORYTELLING_PLUGIN_NAME)
        if storytelling_plugin and "GenerateContent" in storytelling_plugin:
            result: FunctionResult = await storytelling_plugin["GenerateContent"].invoke(
                kernel,
                KernelArguments(
                    prompt=prompt,
                    execution_settings=execution_settings
                )
            )
        else:
            # Fallback to narrative generation function
            result: FunctionResult = await generate_act_narrative_only_function.invoke(
                kernel,
                KernelArguments(
                    user_instruction=prompt,
                    execution_settings=execution_settings
                )
            )
        
        if result.value:
            # Extract clean text content from the result
            excerpt_text = extract_text_from_result(result)
            
            # Track cost
            await log_ai_streaming_call(
                user_id=current_user.id,
                model_config=model_settings,
                input_prompt=prompt,
                output_text=excerpt_text,
                call_type="blog_excerpt_generation",
                db=db
            )
            
            excerpt = excerpt_text.strip().strip('"').strip("'")
            
            await blog_writing_manager.send_message(session_id, {
                "type": "excerpt_generated",
                "excerpt": excerpt,
                "character_count": len(excerpt)
            })
        else:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to generate excerpt"
            })
    
    except Exception as e:
        logger.error(f"Error generating blog excerpt: {e}")
        await blog_writing_manager.send_message(session_id, {
            "type": "error",
            "message": "Failed to generate excerpt"
        })


async def handle_suggest_tags(
    session_id: str,
    message: Dict[str, Any],
    current_user: User,
    db: AsyncSession
):
    """Suggest relevant tags for blog content."""
    
    try:
        content = message.get("content", "")
        title = message.get("title", "")
        
        if not content and not title:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Content or title is required"
            })
            return
        
        # Get existing tags from database
        existing_tags_result = await db.execute(
            select(BlogTag.name).order_by(BlogTag.usage_count.desc()).limit(100)
        )
        existing_tags = [tag[0] for tag in existing_tags_result.fetchall()]
        
        # Generate prompt using prompt service
        prompt = BlogPromptService.format_suggest_tags_prompt(
            content=content,
            title=title,
            existing_tags=existing_tags
        )
        
        if not prompt:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to load tag suggestion prompt"
            })
            return
        
        # Send "thinking" message
        await blog_writing_manager.send_message(session_id, {
            "type": "thinking",
            "message": "Analyzing content for tags..."
        })
        
        # Generate tag suggestions
        storytelling_plugin = kernel.plugins.get(STORYTELLING_PLUGIN_NAME)
        if storytelling_plugin and "AnalyzeContent" in storytelling_plugin:
            result: FunctionResult = await storytelling_plugin["AnalyzeContent"].invoke(
                kernel,
                KernelArguments(
                    prompt=prompt,
                    execution_settings=OpenAIChatPromptExecutionSettings(
                        max_tokens=150,
                        temperature=0.5,
                        top_p=0.9
                    )
                )
            )
        else:
            # Fallback to narrative generation function
            result: FunctionResult = await generate_act_narrative_only_function.invoke(
                kernel,
                KernelArguments(
                    user_instruction=prompt,
                    execution_settings=OpenAIChatPromptExecutionSettings(
                        max_tokens=150,
                        temperature=0.5,
                        top_p=0.9
                    )
                )
            )
        
        if result.value:
            # Extract clean text content from the result
            tags_text = extract_text_from_result(result).strip()
            
            # Parse tags from response
            suggested_tags = [tag.strip() for tag in tags_text.split(',')]
            suggested_tags = [tag for tag in suggested_tags if tag and len(tag) > 1]
            
            await blog_writing_manager.send_message(session_id, {
                "type": "tags_suggested",
                "suggested_tags": suggested_tags[:8],  # Limit to 8 tags
                "existing_tags": existing_tags[:20]  # Provide existing tags for reference
            })
        else:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to suggest tags"
            })
    
    except Exception as e:
        logger.error(f"Error suggesting blog tags: {e}")
        await blog_writing_manager.send_message(session_id, {
            "type": "error",
            "message": "Failed to suggest tags"
        })


async def handle_get_writing_tips(
    session_id: str,
    message: Dict[str, Any],
    current_user: User,
    db: AsyncSession
):
    """Get writing tips and suggestions."""
    
    try:
        content = message.get("content", "")
        tip_type = message.get("tip_type", "general")
        
        # Generate prompt using prompt service
        prompt = BlogPromptService.format_writing_tips_prompt(
            content=content,
            tip_type=tip_type
        )
        
        if not prompt:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to load writing tips prompt"
            })
            return
        
        # Send "thinking" message
        await blog_writing_manager.send_message(session_id, {
            "type": "thinking",
            "message": f"Preparing {tip_type} writing tips..."
        })
        
        # Generate tips
        storytelling_plugin = kernel.plugins.get(STORYTELLING_PLUGIN_NAME)
        if storytelling_plugin and "GenerateContent" in storytelling_plugin:
            result: FunctionResult = await storytelling_plugin["GenerateContent"].invoke(
                kernel,
                KernelArguments(
                    prompt=prompt,
                    execution_settings=OpenAIChatPromptExecutionSettings(
                        max_tokens=400,
                        temperature=0.7,
                        top_p=0.9
                    )
                )
            )
        else:
            # Fallback to narrative generation function
            result: FunctionResult = await generate_act_narrative_only_function.invoke(
                kernel,
                KernelArguments(
                    user_instruction=prompt,
                    execution_settings=OpenAIChatPromptExecutionSettings(
                        max_tokens=400,
                        temperature=0.7,
                        top_p=0.9
                    )
                )
            )
        
        if result.value:
            # Extract clean text content from the result
            tips_text = extract_text_from_result(result)
            
            await blog_writing_manager.send_message(session_id, {
                "type": "writing_tips",
                "tips": tips_text,
                "tip_type": tip_type
            })
        else:
            await blog_writing_manager.send_message(session_id, {
                "type": "error",
                "message": "Failed to generate writing tips"
            })
    
    except Exception as e:
        logger.error(f"Error getting writing tips: {e}")
        await blog_writing_manager.send_message(session_id, {
            "type": "error",
            "message": "Failed to get writing tips"
        })
