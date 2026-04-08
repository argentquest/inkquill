"""Service helpers for world chat service."""

# /story_app/app/services/world_chat_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import UTC, datetime
import json

# Core imports
from app.core.storage_deps import LocalStorageClient, build_storage_url
from app.services.world_context_loader import WorldContextLoader
from app.services.direct_context import build_document_context, build_structured_world_context
from app.services.cost_tracker_service import CostTrackerService
from app.services.ai_client_factory import AIClientFactory
from app.services.temperature_optimizer import TemperatureOptimizer, TaskType
from app.services import langgraph_runtime_setup
from app.services.langgraph_kernel import KernelArguments, LangGraphKernel as Kernel
from app.core.config import settings
from app.crud import chat_session as chat_session_crud
from app.crud import chat_message as chat_message_crud
from app.crud import ai_model_config as ai_model_crud
from app.services.ai_model_cache import model_cache
from app.schemas.chat import (
    ChatSessionCreate, 
    SendMessageRequest, 
    SendMessageResponse,
    ChatMessageCreate,
    ChatMessageRead
)

logger = logging.getLogger(__name__)


class WorldChatService:
    """Service for handling chat interactions with world context"""
    
    def __init__(self, db: AsyncSession, blob_service_client: Optional[LocalStorageClient] = None):
        self.db = db
        self.blob_service_client = blob_service_client
        self.context_loader = WorldContextLoader(db, blob_service_client)
        self.cost_tracker = CostTrackerService(db)
        # Use the shared storytelling runtime kernel.
    
    async def create_chat_session(self, world_id: int, user_id: int) -> int:
        """Create a new chat session with auto-generated title"""
        try:
            # Load world to get name for title
            world_context = await self.context_loader.load_full_world_context(world_id, user_id)
            if not world_context:
                raise ValueError(f"World {world_id} not found")
            
            world_name = world_context.world.get("name", "Unknown World")
            title = f"Chat about {world_name} - {datetime.now().strftime('%b %d, %Y %I:%M %p')}"
            
            session_create = ChatSessionCreate(
                world_id=world_id,
                title=title
            )
            
            session = await chat_session_crud.create_chat_session(
                self.db, session_create, user_id
            )
            
            logger.info(f"Created chat session {session.id} for world {world_id}")
            return session.id
            
        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            raise
    
    async def send_message(
        self, 
        session_id: int, 
        user_id: int, 
        request: SendMessageRequest,
        public_chat: bool = False
    ) -> SendMessageResponse:
        """Process a user message and generate AI response"""
        try:
            # Verify session belongs to user
            session = await chat_session_crud.get_chat_session(self.db, session_id, user_id)
            if not session:
                raise ValueError(f"Chat session {session_id} not found")
            
            # Load world context
            world_context = await self.context_loader.load_full_world_context(
                session.world_id, user_id, public_chat
            )
            if not world_context:
                raise ValueError(f"World {session.world_id} not found")
            
            # Get conversation history
            conversation_history = await chat_message_crud.get_conversation_context(
                self.db, session_id, limit=20
            )
            
            # Get AI model configuration
            ai_model_config = None
            if public_chat:
                # HARDCODED: Always use GPT-4.1 Mini (Next Generation) for public chat (model ID 9)
                hardcoded_model_id = 9  # GPT-4.1 Mini (Next Generation)
                
                # First check model cache
                if hardcoded_model_id in model_cache.configurations:
                    ai_model_config = model_cache.configurations[hardcoded_model_id]
                    logger.info(f"Using HARDCODED GPT-4.1 Mini (model ID {hardcoded_model_id}) from cache for public chat")
                else:
                    # Fallback to database query if not in cache
                    ai_model_config = await ai_model_crud.get_model_config_by_id(
                        self.db, hardcoded_model_id
                    )
                    if not ai_model_config:
                        logger.warning(
                            "HARDCODED public chat model ID %s not found; falling back to default model",
                            hardcoded_model_id,
                        )
                        ai_model_config = await ai_model_crud.get_default_model_config(self.db)
                    else:
                        logger.info(
                            "Using HARDCODED GPT-4.1 Mini (model ID %s) from database for public chat",
                            hardcoded_model_id,
                        )
            elif request.ai_model_config_id:
                ai_model_config = await ai_model_crud.get_model_config_by_id(
                    self.db, request.ai_model_config_id
                )
            else:
                # For authenticated users when no config specified, use default model
                ai_model_config = await ai_model_crud.get_default_model_config(self.db)
            
            # Create user message
            user_message_data = ChatMessageCreate(
                role="user",
                content=request.message,
                element_type=request.element_type,
                element_id=request.element_id
            )
            user_message = await chat_message_crud.create_chat_message(
                self.db, user_message_data, session_id
            )
            
            # Generate AI response
            ai_response_content, cost_log_id, full_context, call_stats = await self._generate_ai_response(
                user_message=request.message,
                world_context=world_context,
                conversation_history=conversation_history,
                element_type=request.element_type,
                element_id=request.element_id,
                user_id=user_id,
                ai_model_config=ai_model_config,
                world_id=session.world_id,
                public_chat=public_chat
            )
            
            # Create AI message
            ai_message_data = ChatMessageCreate(
                role="assistant",
                content=ai_response_content,
                full_context=full_context,
                element_type=request.element_type,
                element_id=request.element_id
            )
            ai_message = await chat_message_crud.create_chat_message(
                self.db, ai_message_data, session_id, cost_log_id
            )
            
            # Update session timestamp
            await chat_session_crud.touch_session_updated_at(self.db, session_id)
            
            logger.info(f"Processed message in session {session_id}")
            
            # Import the AICallStats schema
            from app.schemas.chat import AICallStats
            
            return SendMessageResponse(
                user_message=ChatMessageRead.model_validate(user_message),
                ai_response=ChatMessageRead.model_validate(ai_message),
                session_updated_at=datetime.now(UTC),
                call_stats=AICallStats(**call_stats) if call_stats else None
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise
    
    async def _generate_ai_response(
        self,
        user_message: str,
        world_context: Any,
        conversation_history: List[Any],
        element_type: Optional[str],
        element_id: Optional[int],
        user_id: int,
        ai_model_config: Optional[Any],
        world_id: int,
        public_chat: bool = False
    ) -> Tuple[str, Optional[int], Dict[str, Any], Dict[str, Any]]:
        """Generate AI response using direct structured context."""
        try:
            document_context, context_sources = await self._get_document_context(
                user_message, world_context, element_type, element_id
            )
            
            # Build conversation context
            conversation_context = self._build_conversation_context(
                conversation_history, user_message
            )
            
            # Build world context summary
            world_summary = self._build_world_summary(world_context)
            
            # Prepare element-specific context
            element_context = ""
            if element_type and element_id:
                element_data = await self.context_loader.get_element_by_id(
                    element_type, element_id, world_context.world["id"]
                )
                if element_data:
                    element_context = f"\n\nFOCUS ELEMENT ({element_type.upper()}):\n{json.dumps(element_data, indent=2)}"
            
            # Create full context for AI
            full_context = {
                "user_message": user_message,
                "world_summary": world_summary,
                "document_context": document_context,
                "context_sources": context_sources,
                "conversation_history": conversation_context,
                "element_context": element_context,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            # Debug: Log context sizes
            logger.info(f"[AI GENERATION DEBUG] Context sizes:")
            logger.info(f"[AI GENERATION DEBUG]   - World summary: {len(world_summary)} chars")
            logger.info(f"[AI GENERATION DEBUG]   - Document context: {len(document_context)} chars")
            logger.info(f"[AI GENERATION DEBUG]   - Conversation history: {len(conversation_context)} chars")
            logger.info(f"[AI GENERATION DEBUG]   - Element context: {len(element_context)} chars")
            
            # Build system prompt
            system_prompt = self._build_system_prompt(
                world_summary, document_context, element_context
            )
            
            logger.info(f"[AI GENERATION DEBUG] System prompt length: {len(system_prompt)} chars")
            
            # Get kernel with model configuration
            kernel = await self._get_configured_kernel(ai_model_config)
            
            # Prepare arguments
            arguments = KernelArguments(
                system_prompt=system_prompt,
                conversation_history=conversation_context,
                user_message=user_message
            )
            
            # Generate response using AI client factory
            try:
                import time
                
                # Create client based on model provider
                client = AIClientFactory.create_client_for_model(ai_model_config)
                
                # Build full prompt for logging
                full_prompt = f"System: {system_prompt}\n\nConversation History:\n{conversation_context}\n\nUser: {user_message}"
                
                # Time the AI call
                start_time = time.perf_counter()
                
                # Use the model configuration from database with provider-aware name resolution
                model_name = AIClientFactory.resolve_model_name(ai_model_config) if ai_model_config else settings.DEFAULT_GENERATION_MODEL_NAME
                max_tokens = ai_model_config.max_tokens if ai_model_config else 1000
                base_temperature = ai_model_config.temperature if ai_model_config else 0.7
                
                # --- Optimize temperature for chat context ---
                if ai_model_config:
                    optimal_temperature, temp_explanation = TemperatureOptimizer.optimize_for_chat(
                        model_name=ai_model_config.model_name,
                        user_message=user_message,
                        base_temperature=base_temperature,
                        world_context={"world_name": world_context.world.get("name", "")}
                    )
                    logger.info(f"Chat temperature optimization: {temp_explanation}")
                    temperature = optimal_temperature
                else:
                    temperature = base_temperature
                
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{conversation_context}\n\nUser: {user_message}"}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                end_time = time.perf_counter()
                duration_ms = int((end_time - start_time) * 1000)
                
                # Debug the raw response
                logger.debug(f"Raw API response: choices={len(response.choices)}, message={response.choices[0].message}")
                message = response.choices[0].message
                raw_content = message.content
                reasoning_content = getattr(message, 'reasoning_content', None)
                logger.debug(f"Raw content: {repr(raw_content)}")
                logger.debug(f"Reasoning content: {repr(reasoning_content)}")
                
                # DeepSeek models may return response in reasoning_content instead of content
                ai_response = raw_content or reasoning_content or "No response generated."
                logger.info(f"Successfully generated AI response for world chat in {duration_ms}ms")
                logger.debug(f"AI response content: {ai_response[:200]}..." if len(ai_response) > 200 else f"AI response content: {ai_response}")
                
            except Exception as e:
                logger.error(f"Error with chat completion: {e}")
                ai_response = "I apologize, but I'm having trouble generating a response right now. Please try again."
                duration_ms = 0
                full_prompt = f"System: {system_prompt}\n\nUser: {user_message}"  # Fallback prompt
            
            # AI response is already extracted above
            
            # Track cost - always log for both authenticated and anonymous users
            cost_log_id = None
            input_tokens = 0
            output_tokens = 0
            total_cost = 0.0
            
            if ai_model_config:
                # Estimate tokens (simplified) with null checks
                input_tokens = len(full_prompt or "") // 4
                output_tokens = len(ai_response or "") // 4
                
                # Calculate cost using the model's pricing (costs are per million tokens)
                from decimal import Decimal
                input_cost = Decimal(str(input_tokens)) * Decimal(str(ai_model_config.user_price_input_usd_pm)) / Decimal('1000000')
                output_cost = Decimal(str(output_tokens)) * Decimal(str(ai_model_config.user_price_output_usd_pm)) / Decimal('1000000')
                total_cost = float(input_cost + output_cost)
                
                cost_log_id = await self.cost_tracker.log_ai_call(
                    user_id=user_id,
                    model_config=ai_model_config,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    operation_type="anonymous_world_chat" if public_chat else "world_chat",
                    input_prompt=full_prompt,
                    duration_ms=duration_ms,
                    object_id=world_id
                )
            else:
                logger.warning(f"No AI model config found for cost tracking - user {user_id}, world {world_id}")
            
            # Return statistics along with response
            call_stats = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost": total_cost,
                "model_name": ai_model_config.display_name if ai_model_config else "Unknown",
                "duration_ms": duration_ms
            }
            
            return ai_response, cost_log_id, full_context, call_stats
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            raise
    
    async def _get_document_context(
        self, 
        user_message: str, 
        world_context: Any, 
        element_type: Optional[str], 
        element_id: Optional[int]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Build relevant context directly from uploaded documents."""
        try:
            search_query = user_message
            if element_type and element_id:
                element_data = await self.context_loader.get_element_by_id(
                    element_type, element_id, world_context.world["id"]
                )
                if element_data:
                    search_query += f" {element_data.get('name', '')} {element_data.get('title', '')}"

            context_text, sources = await build_document_context(
                self.db,
                world_context.world["id"],
                search_query,
                max_documents=3,
                max_chars_per_document=1200,
            )

            logger.info("[DIRECT CONTEXT] Prepared %s document sources", len(sources))
            return context_text, sources
            
        except Exception as e:
            logger.error("[DIRECT CONTEXT] Error building document context: %s", str(e), exc_info=True)
            return "Document context unavailable.", []
    
    def _build_conversation_context(
        self, 
        conversation_history: List[Any], 
        current_message: str
    ) -> str:
        """Build conversation context string"""
        context_parts = []
        
        for message in conversation_history[-10:]:  # Last 10 messages
            role = "User" if message.role == "user" else "Assistant"
            context_parts.append(f"{role}: {message.content}")
        
        context_parts.append(f"User: {current_message}")
        
        return "\n".join(context_parts)
    
    def _build_world_summary(self, world_context: Any) -> str:
        return build_structured_world_context(world_context)
    
    def _build_system_prompt(
        self, 
        world_summary: str, 
        document_context: str, 
        element_context: str
    ) -> str:
        """Build the system prompt for the AI"""
        return f"""You are an AI assistant helping a user explore and discuss their creative world. 

WORLD CONTEXT:
{world_summary}

UPLOADED DOCUMENT CONTEXT:
{document_context}
{element_context}

INSTRUCTIONS:
1. You have access to complete information about this world including all characters, locations, lore, stories, acts, and scenes
2. Answer questions about the world elements and their relationships
3. Suggest new elements, plot developments, or creative ideas when appropriate
4. Help identify plot holes, inconsistencies, or opportunities for development
5. Maintain consistency with established world lore and character personalities
6. If asked about creating new elements, provide detailed suggestions that fit the world's tone and genre
7. Be conversational and engaging while being informative
8. When discussing specific elements, reference their relationships to other elements in the world

Remember: You can suggest new characters, locations, lore items, or story developments that would enhance the world."""
    
    async def _get_configured_kernel(self, ai_model_config: Optional[Any]) -> Kernel:
        """Get a configured storytelling runtime instance."""
        try:
            # Use the shared storytelling runtime kernel.
            # In a more sophisticated implementation, you could configure model-specific settings here
            kernel = langgraph_runtime_setup.kernel
            
            # Register the world chat plugin
            await self._register_world_chat_plugin(kernel)
            
            return kernel
            
        except Exception as e:
            logger.error(f"Error configuring kernel: {str(e)}")
            raise
    
    async def _register_world_chat_plugin(self, kernel: Kernel):
        """Register the world chat plugin with the kernel"""
        try:
            # This would register custom world chat functions
            # For now, we'll use a simple chat function
            pass
        except Exception as e:
            logger.error(f"Error registering world chat plugin: {str(e)}")
            raise

