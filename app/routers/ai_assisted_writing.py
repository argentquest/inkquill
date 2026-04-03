"""API routes for ai assisted writing."""

# /story_app/app/routers/ai_scene_writing.py

from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, Depends
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
from app.models.story import Story
from app.models.act import Act
from app.models.scene import Scene
from app.crud import story as crud_story, act as crud_act, scene as crud_scene
from app.crud import character as crud_character, location as crud_location, lore_item as crud_lore_item
from app.core.deps_ws import get_current_user_from_ws_ticket
from app.core.config import settings
from app.services.ai_model_cache import model_cache
from app.services.sk_kernel_instance import (
    kernel,
    generate_scene_narrative_only_function, 
    generate_scene_metadata_function,      
)
from app.services.cost_tracker_service import log_ai_call, log_ai_streaming_call, get_usage_from_sk_result
from app.services.temperature_optimizer import TemperatureOptimizer, TaskType
from app.services.direct_context import build_document_context
from openai import APIError
from markdownify import markdownify as md

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["ai-scene-writing"],
)

class SceneConnectionManager:
    """Response or helper model for scene connection manager."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"Scene WS connected: {connection_id} (Total: {len(self.active_connections)})")
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            self.active_connections.pop(connection_id)
            logger.info(f"Scene WS disconnected: {connection_id} (Total: {len(self.active_connections)})")
    async def send_json_message(self, data: Dict, connection_id: str):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending Scene WS JSON message to {connection_id}: {e}", exc_info=True)
                self.disconnect(connection_id)

scene_ws_manager = SceneConnectionManager()

def format_linked_elements_for_prompt(elements: List[Dict[str, Any]], element_type_name: str, name_field: str, role_field: str, max_elements: int = 7) -> str:
    """Provide internal router support for format linked elements for prompt."""
    if not elements: return f"No specific {element_type_name}s are linked to this story."
    
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


@router.websocket("/ws/stories/{story_id}/acts/{act_id}/scenes/{scene_id}/generate")
async def websocket_scene_content_generator(
    websocket: WebSocket,
    story_id: int,
    act_id: int,
    scene_id: int, 
    current_user: User = Depends(get_current_user_from_ws_ticket),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle WEBSOCKET /ws/stories/{story_id}/acts/{act_id}/scenes/{scene_id}/generate."""
    connection_id = f"scene_ws_s{story_id}_a{act_id}_sc{scene_id}_{current_user.username}"
    await scene_ws_manager.connect(websocket, connection_id)

    # --- Start: Context Fetching ---
    story_obj: Optional[Story] = None
    parent_act_obj: Optional[Act] = None
    current_scene_obj: Optional[Scene] = None
    try: 
        story_obj = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
        parent_act_obj = await crud_act.get_act(db, act_id=act_id)
        current_scene_obj = await crud_scene.get_scene(db, scene_id=scene_id)
        if not all([story_obj, parent_act_obj, current_scene_obj]) or parent_act_obj.story_id != story_id or current_scene_obj.act_id != act_id:
            raise Exception("Context mismatch or not found.")
    except Exception as e: 
        logger.error(f"Error fetching initial context for Scene WS {connection_id}: {e}", exc_info=True)
        await scene_ws_manager.send_json_message({"type": "error", "data": "Context load error."}, connection_id)
        if websocket.client_state != WebSocketState.DISCONNECTED: await websocket.close()
        scene_ws_manager.disconnect(connection_id); return
    # --- End: Context Fetching ---

    try: 
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_instruction = message_data.get("user_instruction_for_scene")
            scene_current_html = message_data.get("scene_current_content", "")
            generation_mode = message_data.get("generation_mode", "Continue/Append")
            selected_text = message_data.get("selected_text", "")
            model_config_id = message_data.get("model_config_id")

            # Convert model_config_id to int safely
            if model_config_id:
                try:
                    model_config_id_int = int(model_config_id)
                    model_config_to_use = model_cache.configurations.get(model_config_id_int)
                except (ValueError, TypeError):
                    await scene_ws_manager.send_json_message({"type": "error", "data": f"Invalid model ID: {model_config_id}"}, connection_id)
                    continue
            else:
                model_config_to_use = model_cache.default_generation_model
            if not model_config_to_use:
                await scene_ws_manager.send_json_message({"type": "error", "data": "No active AI models configured."}, connection_id)
                continue
            
            logger.info(f"Scene WS {connection_id}: Using model '{model_config_to_use.display_name}' for generation.")

            # --- Optimize temperature based on user instruction and model capabilities ---
            optimal_temperature, detected_task, temp_explanation = TemperatureOptimizer.optimize_for_writing_assistant(
                model_name=model_config_to_use.model_name,
                user_instruction=user_instruction,
                base_temperature=model_config_to_use.temperature,
                current_content=scene_current_html,
                generation_mode=generation_mode
            )
            
            logger.info(f"Scene WS {connection_id}: Temperature optimization: {temp_explanation}")

            # --- Full Context Building ---
            story_summary_for_prompt = story_obj.short_description or "No story summary provided."
            parent_act_summary_for_prompt = parent_act_obj.act_summary or "No summary for the parent act."
            current_scene_summary_text = current_scene_obj.summary or "Not specified."
            scene_current_content_for_ai = md(scene_current_html) if scene_current_html and scene_current_html.strip() else "No current content."
            scene_system_prompt_content = current_scene_obj.story_class.description if current_scene_obj.story_class and current_scene_obj.story_class.description else "Default writing style."
            
            summaries_of_last_two_acts_text = "This is the first act."
            # ... (Full logic to fetch and format previous acts would go here) ...
            
            previous_scenes_full_content_text = "This is the first scene in this act."
            # ... (Full logic to fetch and format previous scenes would go here) ...
            
            linked_chars = await crud_character.get_characters_for_story(db, story_id=story_id)
            linked_locs = await crud_location.get_locations_for_story(db, story_id=story_id)
            linked_lore = await crud_lore_item.get_lore_items_for_story(db, story_id=story_id)
            linked_characters_context_str = format_linked_elements_for_prompt(linked_chars, "Character", "name", "role_in_story")
            linked_locations_context_str = format_linked_elements_for_prompt(linked_locs, "Location", "name", "significance_to_story")
            linked_lore_items_context_str = format_linked_elements_for_prompt(linked_lore, "Lore Item", "title", "relevance_to_story")
            
            document_context_for_scene = "No uploaded document context available."
            try:
                if user_instruction:
                    search_query = f"{user_instruction} {story_obj.title}"
                    if current_scene_obj.title:
                        search_query += f" {current_scene_obj.title}"
                    if parent_act_obj.title:
                        search_query += f" {parent_act_obj.title}"
                    if current_scene_obj.summary:
                        search_query += f" {current_scene_obj.summary}"
                    document_context_for_scene, _ = await build_document_context(
                        db,
                        story_obj.world_id,
                        search_query,
                        max_documents=3,
                        max_chars_per_document=1500,
                    )
                    logger.info(f"Scene WS {connection_id}: Prepared direct document context for query: '{search_query[:100]}...'")
                    
            except Exception as context_error:
                logger.error(f"Scene WS {connection_id}: Error preparing direct document context: {context_error}", exc_info=True)
                document_context_for_scene = "Error preparing document context - proceeding with available information."

            try:
                narrative_exec_settings = OpenAIChatPromptExecutionSettings(
                    service_id=model_config_to_use.model_name,
                    max_tokens=model_config_to_use.max_tokens,
                    temperature=optimal_temperature,  # Use optimized temperature instead of base
                    top_p=model_config_to_use.top_p,
                    presence_penalty=model_config_to_use.presence_penalty,
                    frequency_penalty=model_config_to_use.frequency_penalty
                )
                
                kernel_args_narrative = KernelArguments(
                    settings=narrative_exec_settings,
                    generation_mode=generation_mode,
                    story_title=story_obj.title,
                    story_summary=story_summary_for_prompt,
                    parent_act_number=str(parent_act_obj.act_number),
                    parent_act_title=parent_act_obj.title,
                    parent_act_summary=parent_act_summary_for_prompt,
                    scene_number=str(current_scene_obj.scene_number),
                    scene_title=current_scene_obj.title or "Untitled Scene",
                    current_scene_summary=current_scene_summary_text,
                    scene_current_content=scene_current_content_for_ai,
                    selected_text=selected_text,
                    summaries_of_last_two_acts=summaries_of_last_two_acts_text,
                    previous_scenes_full_content_in_act=previous_scenes_full_content_text,
                    scene_system_prompt_content=scene_system_prompt_content,
                    linked_characters_context=linked_characters_context_str,
                    linked_locations_context=linked_locations_context_str,
                    linked_lore_items_context=linked_lore_items_context_str,
                    document_context_for_scene=document_context_for_scene,
                    user_instruction_for_scene=user_instruction
                )
                
                await scene_ws_manager.send_json_message({"type": "narrative_generation_start"}, connection_id)
                full_narrative_text_accumulated = ""
                narrative_start_time = time.perf_counter()
                
                async for stream_item in kernel.invoke_stream(generate_scene_narrative_only_function, kernel_args_narrative):
                    chunk = str(stream_item[0]) if stream_item else ""
                    if chunk:
                        full_narrative_text_accumulated += chunk
                        await scene_ws_manager.send_json_message({"type": "narrative_content_chunk", "data": chunk}, connection_id)
                
                narrative_end_time = time.perf_counter()
                await scene_ws_manager.send_json_message({"type": "narrative_generation_end"}, connection_id)
                
                # Log the narrative generation call with token estimation
                if full_narrative_text_accumulated.strip():
                    narrative_duration_ms = int((narrative_end_time - narrative_start_time) * 1000)
                    await log_ai_streaming_call(
                        user_id=current_user.id,
                        model_config=model_config_to_use,
                        input_prompt=user_instruction,
                        output_text=full_narrative_text_accumulated,
                        call_type="scene_narrative_generation",
                        duration_ms=narrative_duration_ms,
                        object_id=scene_id,
                        db=db
                    )

                if full_narrative_text_accumulated.strip() and generate_scene_metadata_function:
                    metadata_model_config = next((c for c in model_cache.generation_models.values() if c.is_json_mode), model_config_to_use)
                    
                    metadata_exec_settings = OpenAIChatPromptExecutionSettings(
                        service_id=metadata_model_config.model_name,
                        max_tokens=metadata_model_config.max_tokens,
                        temperature=metadata_model_config.temperature,
                        response_format={"type": "json_object"}
                    )
                    
                    kernel_args_metadata = KernelArguments(
                        scene_full_narrative_text=full_narrative_text_accumulated,
                        settings=metadata_exec_settings
                    )
                    
                    start_time = time.perf_counter()
                    metadata_result_obj: FunctionResult = await kernel.invoke(generate_scene_metadata_function, kernel_args_metadata)
                    end_time = time.perf_counter()
                    
                    usage_data = get_usage_from_sk_result(metadata_result_obj)
                    logger.info(f"Scene metadata SK result metadata: {metadata_result_obj.metadata}")
                    logger.info(f"Scene metadata usage data extracted: {usage_data}")
                    
                    if usage_data:
                        await log_ai_call(
                            user_id=current_user.id,
                            model_config=metadata_model_config,
                            usage=usage_data,
                            call_type="scene_metadata_generation",
                            input_prompt=user_instruction,
                            duration_ms=int((end_time - start_time) * 1000),
                            object_id=scene_id,
                            db=db
                        )
                        logger.info(f"Scene metadata cost logged successfully")
                    else:
                        logger.warning(f"No usage data found for scene metadata generation - cannot log cost")
                    
                    metadata_json_str = str(metadata_result_obj.value[0])
                    await scene_ws_manager.send_json_message({"type": "metadata_result", "data": metadata_json_str}, connection_id)
            
            except (APIError, Exception) as e_sk:
                error_msg = f"AI service error: {str(e_sk)}"
                logger.error(f"Error during SK invocation for Scene WS {connection_id}: {e_sk}", exc_info=True)
                await scene_ws_manager.send_json_message({"type": "error", "data": error_msg}, connection_id)
    
    except WebSocketDisconnect:
        logger.info(f"Scene WS Client {connection_id} disconnected.")
    except Exception as e_ws_loop:
        logger.error(f"Unexpected Scene WebSocket loop error for {connection_id}: {e_ws_loop}", exc_info=True)
    finally:
        scene_ws_manager.disconnect(connection_id)

