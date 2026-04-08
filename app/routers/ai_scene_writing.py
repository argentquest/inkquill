"""API routes for ai scene writing."""

# /story_app/app/routers/ai_assisted_writing.py

from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, Depends
)
from fastapi.websockets import WebSocketState 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json 
import time
from typing import Dict, Any, Optional, List
import logging

from app.core.deps import get_db_session
from app.models.user import User 
from app.models.story import Story
from app.models.act import Act
from app.crud import story as crud_story, act as crud_act
from app.crud import character as crud_character, location as crud_location, lore_item as crud_lore_item
from app.core.deps_ws import get_current_user_from_ws_ticket
from app.core.config import settings
from app.services.ai_model_cache import model_cache
from app.services.storytelling_runtime import (
    kernel,
    generate_act_narrative_only_function, 
    generate_act_metadata_function,      
)
from app.services.cost_tracker_service import log_ai_call, log_ai_streaming_call, get_usage_from_sk_result
from app.services.temperature_optimizer import TemperatureOptimizer, TaskType
from app.services.direct_context import build_document_context
from app.services.langgraph_kernel import OpenAIChatPromptExecutionSettings, KernelArguments, FunctionResult
from openai import APIError
from markdownify import markdownify as md

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai-assisted-writing"])

class ActConnectionManager:
    """Response or helper model for act connection manager."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"Act AI WS connected: {connection_id} (Total: {len(self.active_connections)})")
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            self.active_connections.pop(connection_id)
            logger.info(f"Act AI WS disconnected: {connection_id} (Total: {len(self.active_connections)})")
    async def send_json_message(self, data: Dict, connection_id: str):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending Act AI WS JSON message to {connection_id}: {e}", exc_info=True)
                self.disconnect(connection_id)

act_ws_manager = ActConnectionManager()

def format_linked_elements_for_prompt(elements: List[Dict[str, Any]], element_type_name: str, name_field: str, role_field: str, max_elements: int = 7) -> str:
    """Provide internal router support for format linked elements for prompt."""
    if not elements: return f"No specific {element_type_name}s linked."
    formatted_list = []
    for i, el_data in enumerate(elements):
        if i >= max_elements:
            formatted_list.append(f"- ...and {len(elements) - max_elements} more.")
            break
        
        element_key = element_type_name.lower().replace(" ", "_")
        if "item" in element_key: element_key = "lore_item"
        
        el_obj = el_data.get(element_key)
        if not el_obj: continue

        name = getattr(el_obj, name_field, "Unnamed Element")
        role = el_data.get(role_field, "Role not specified")
        description = getattr(el_obj, 'description', '') or ""
        desc_snippet = f" (Desc: {description.strip()[:75]}...)" if description and description.strip() else ""
        
        # Add AI import fields if available
        additional_info = []
        if hasattr(el_obj, 'relationships') and el_obj.relationships:
            additional_info.append(f"Relationships: {el_obj.relationships[:50]}...")
        if hasattr(el_obj, 'geography') and el_obj.geography:
            additional_info.append(f"Geography: {el_obj.geography[:50]}...")
        if hasattr(el_obj, 'cultural_context') and el_obj.cultural_context:
            additional_info.append(f"Culture: {el_obj.cultural_context[:50]}...")
        if hasattr(el_obj, 'connected_elements') and el_obj.connected_elements:
            additional_info.append(f"Connections: {el_obj.connected_elements[:50]}...")
        if hasattr(el_obj, 'related_elements') and el_obj.related_elements:
            additional_info.append(f"Related: {el_obj.related_elements[:50]}...")
        
        additional_context = f" [{', '.join(additional_info)}]" if additional_info else ""
        formatted_list.append(f"- {name} (Role/Relevance: {role}){desc_snippet}{additional_context}")
    return f"Key {element_type_name}s for this Story:\n" + "\n".join(formatted_list)


@router.websocket("/ws/stories/{story_id}/acts/{act_id}/generate")
async def websocket_act_content_generator(
    websocket: WebSocket, story_id: int, act_id: int,
    current_user: User = Depends(get_current_user_from_ws_ticket), 
    db: AsyncSession = Depends(get_db_session)
):
    """Handle WEBSOCKET /ws/stories/{story_id}/acts/{act_id}/generate."""
    connection_id = f"act_ws_s{story_id}_a{act_id}_{current_user.username}"
    await act_ws_manager.connect(websocket, connection_id)
    
    story_obj: Optional[Story] = None
    act_obj: Optional[Act] = None
    try:
        story_obj = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
        act_obj = await crud_act.get_act(db, act_id=act_id)
        if not story_obj or not act_obj or act_obj.story_id != story_obj.id:
            raise Exception("Context mismatch or not found.")
    except Exception as e:
        logger.error(f"Error fetching initial context for Act WS {connection_id}: {e}", exc_info=True)
        await act_ws_manager.send_json_message({"type": "error_act", "data": "Context load error."}, connection_id)
        if websocket.client_state != WebSocketState.DISCONNECTED: await websocket.close()
        act_ws_manager.disconnect(connection_id); return

    try: 
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_instruction = message_data.get("user_instruction")
            current_act_html = message_data.get("current_act_content", "")
            generation_mode = message_data.get("generation_mode", "Continue/Append")
            selected_text = message_data.get("selected_text", "")
            model_config_id = message_data.get("model_config_id")

            # Convert model_config_id to int safely
            if model_config_id:
                try:
                    model_config_id_int = int(model_config_id)
                    model_config_to_use = model_cache.configurations.get(model_config_id_int)
                except (ValueError, TypeError):
                    await act_ws_manager.send_json_message({"type": "error_act", "data": f"Invalid model ID: {model_config_id}"}, connection_id)
                    continue
            else:
                model_config_to_use = model_cache.default_generation_model
            if not model_config_to_use:
                await act_ws_manager.send_json_message({"type": "error_act", "data": "No active AI models configured."}, connection_id)
                continue

            logger.info(f"Act WS {connection_id}: Using model '{model_config_to_use.display_name}' for generation.")
            
            # --- Optimize temperature based on user instruction and model capabilities ---
            optimal_temperature, detected_task, temp_explanation = TemperatureOptimizer.optimize_for_writing_assistant(
                model_name=model_config_to_use.model_name,
                user_instruction=user_instruction,
                base_temperature=model_config_to_use.temperature,
                current_content=current_act_html,
                generation_mode=generation_mode
            )
            
            logger.info(f"Act WS {connection_id}: Temperature optimization: {temp_explanation}")
            
            # --- Build full context for the prompt ---
            story_title_ctx = story_obj.title
            story_description_ctx = story_obj.short_description or "No description."
            previous_acts_summaries_ctx = "This is the first act."
            act_current_content_ctx = md(current_act_html) if current_act_html.strip() else "No current content."
            act_system_prompt_ctx = act_obj.system_prompt.prompt_content if act_obj.system_prompt else "Default writing style."

            linked_chars_ctx = format_linked_elements_for_prompt(await crud_character.get_characters_for_story(db, story_id=story_id), "Character", "name", "role_in_story")
            linked_locs_ctx = format_linked_elements_for_prompt(await crud_location.get_locations_for_story(db, story_id=story_id), "Location", "name", "significance_to_story")
            linked_lore_ctx = format_linked_elements_for_prompt(await crud_lore_item.get_lore_items_for_story(db, story_id=story_id), "Lore Item", "title", "relevance_to_story")
            
            document_context_text = "No uploaded document context available."
            try:
                if user_instruction:
                    search_query = f"{user_instruction} {story_title_ctx}"
                    if act_obj.act_summary:
                        search_query += f" {act_obj.act_summary}"
                    document_context_text, _ = await build_document_context(
                        db,
                        story_obj.world_id,
                        search_query,
                        max_documents=3,
                        max_chars_per_document=1500,
                    )
                    logger.info(f"Act WS {connection_id}: Prepared direct document context for query: '{search_query[:100]}...'")
                    
            except Exception as context_error:
                logger.error(f"Act WS {connection_id}: Error preparing direct document context: {context_error}", exc_info=True)
                document_context_text = "Error preparing document context - proceeding with available information."
            
            try:
                # NARRATIVE GENERATION - Use optimized temperature
                narrative_exec_settings = OpenAIChatPromptExecutionSettings(
                    service_id=model_config_to_use.model_name,
                    max_tokens=model_config_to_use.max_tokens,
                    temperature=optimal_temperature,  # Use optimized temperature instead of base
                    top_p=model_config_to_use.top_p,
                    presence_penalty=model_config_to_use.presence_penalty,
                    frequency_penalty=model_config_to_use.frequency_penalty
                )

                kernel_args_act_narrative = KernelArguments(
                    settings=narrative_exec_settings,
                    generation_mode=generation_mode,
                    story_title=story_title_ctx,
                    story_description=story_description_ctx,
                    previous_acts_summaries=previous_acts_summaries_ctx,
                    act_number=str(act_obj.act_number),
                    act_title=act_obj.title,
                    act_summary=act_obj.act_summary or "No summary.",
                    act_current_content=act_current_content_ctx,
                    selected_text=selected_text,
                    act_system_prompt_content=act_system_prompt_ctx,
                    linked_characters_context=linked_chars_ctx,
                    linked_locations_context=linked_locs_ctx,
                    linked_lore_items_context=linked_lore_ctx,
                    document_context=document_context_text,
                    user_instruction=user_instruction
                )
                
                await act_ws_manager.send_json_message({"type": "narrative_generation_start_act"}, connection_id)
                full_act_narrative_accumulated = ""
                act_narrative_start_time = time.perf_counter()
                
                async for stream_item in kernel.invoke_stream(generate_act_narrative_only_function, kernel_args_act_narrative):
                    chunk = str(stream_item[0]) if stream_item else ""
                    if chunk:
                        full_act_narrative_accumulated += chunk
                        await act_ws_manager.send_json_message({"type": "narrative_content_chunk_act", "data": chunk}, connection_id)
                
                act_narrative_end_time = time.perf_counter()
                await act_ws_manager.send_json_message({"type": "narrative_generation_end_act"}, connection_id)
                
                # Log the act narrative generation call with token estimation
                if full_act_narrative_accumulated.strip():
                    act_narrative_duration_ms = int((act_narrative_end_time - act_narrative_start_time) * 1000)
                    await log_ai_streaming_call(
                        user_id=current_user.id,
                        model_config=model_config_to_use,
                        input_prompt=user_instruction,
                        output_text=full_act_narrative_accumulated,
                        call_type="act_narrative_generation",
                        duration_ms=act_narrative_duration_ms,
                        object_id=act_id,
                        db=db
                    )
                
                # METADATA GENERATION
                if full_act_narrative_accumulated.strip() and generate_act_metadata_function:
                    metadata_model_config = next((c for c in model_cache.generation_models.values() if c.is_json_mode), model_config_to_use)
                    metadata_exec_settings = OpenAIChatPromptExecutionSettings(
                        service_id=metadata_model_config.model_name,
                        max_tokens=metadata_model_config.max_tokens,
                        temperature=metadata_model_config.temperature,
                        response_format={"type": "json_object"}
                    )
                    kernel_args_metadata = KernelArguments(
                        act_full_narrative_text=full_act_narrative_accumulated,
                        settings=metadata_exec_settings
                    )
                    
                    start_time = time.perf_counter()
                    act_metadata_result_obj: FunctionResult = await kernel.invoke(generate_act_metadata_function, kernel_args_metadata)
                    end_time = time.perf_counter()
                    
                    usage_data = get_usage_from_sk_result(act_metadata_result_obj)
                    logger.info(f"Act metadata SK result metadata: {act_metadata_result_obj.metadata}")
                    logger.info(f"Act metadata usage data extracted: {usage_data}")
                    
                    if usage_data:
                        await log_ai_call(
                            user_id=current_user.id,
                            model_config=metadata_model_config,
                            usage=usage_data,
                            call_type="act_metadata_generation",
                            input_prompt=user_instruction,
                            duration_ms=int((end_time - start_time) * 1000),
                            object_id=act_id,
                            db=db
                        )
                        logger.info(f"Act metadata cost logged successfully")
                    else:
                        logger.warning(f"No usage data found for act metadata generation - cannot log cost")
                    
                    metadata_json_str = str(act_metadata_result_obj.value[0])
                    await act_ws_manager.send_json_message({"type": "metadata_result_act", "data": metadata_json_str}, connection_id)

            except (APIError, Exception) as e_sk:
                error_msg = f"AI service error during Act generation: {e_sk}"
                logger.error(f"Act WS {connection_id}: {error_msg}", exc_info=True)
                await act_ws_manager.send_json_message({"type": "error_act", "data": error_msg}, connection_id)
    
    except WebSocketDisconnect:
        logger.info(f"Act WS Client {connection_id} disconnected.")
    except Exception as e_ws_loop:
        logger.error(f"Unexpected Act WebSocket loop error for {connection_id}: {e_ws_loop}", exc_info=True)
    finally:
        act_ws_manager.disconnect(connection_id)

