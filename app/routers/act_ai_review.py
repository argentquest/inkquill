"""API routes for act ai review."""

# /story_app/app/routers/act_ai_review.py

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
import json
import logging
import time
from pydantic import BaseModel, Field

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User as ModelUser
from app.models.act import Act as ModelAct
from app.schemas.ai_review import ActAIReviewResponse
from app.schemas.base import ApiResponse
from app.core.config import settings

# --- FIX: Import the model cache and new dependencies ---
from app.services.ai_model_cache import model_cache
from app.models.ai_model_config import AIModelTypeEnum
from app.services.sk_kernel_instance import kernel
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result
from app.services.sk_constants import STORY_ANALYSIS_PLUGIN_NAME

from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.function_result import FunctionResult
from openai import APIError
from markdownify import markdownify as md
from app.core.dependencies_shared import get_act_and_verify_ownership

# ... (other imports like crud_character, etc., remain the same) ...
from app.crud import character as crud_character, location as crud_location, lore_item as crud_lore_item

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/acts/{act_id}/ai", 
    tags=["act-ai-features"],
    dependencies=[Depends(get_current_active_user)]
)

class AIReviewRequestPayload(BaseModel):
    """Response or helper model for a i review request payload."""
    act_content_to_analyze_override: Optional[str] = Field(None, description="If provided, this content will be used for AI review instead of the act's saved description.")
    # NEW: Allow frontend to request a specific config ID
    model_config_id: Optional[int] = Field(None, description="The ID of the AI Model Configuration to use for this review.")

def convert_html_to_markdown(html_content: Optional[str]) -> str:
    """Convert HTML content to markdown format."""
    if not html_content or not html_content.strip():
        return ""
    return md(html_content, heading_style="ATX", bullets="*").strip()

def _format_linked_elements_for_prompt(elements: List[Dict[str, Any]], element_type_name: str, name_field: str, role_field: str, max_elements: int = 7) -> str:
    """Format linked world elements for AI prompt context."""
    if not elements: 
        return f"No specific {element_type_name}s are linked to this story."
    
    formatted_list = []
    for i, el_data in enumerate(elements):
        if i >= max_elements:
            formatted_list.append(f"- ...and {len(elements) - max_elements} more.")
            break
        
        element_key = element_type_name.lower().replace(" ", "_")
        if "item" in element_key: 
            element_key = "lore_item"
        
        el_obj = el_data.get(element_key)
        if not el_obj: 
            continue

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

@router.post("/review", response_model=ApiResponse, name="trigger_ai_review_for_act_content")
async def trigger_ai_review_for_act_content_api(
    payload: AIReviewRequestPayload, 
    db_act: ModelAct = Depends(get_act_and_verify_ownership), 
    current_user: ModelUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle POST /review."""
    logger.info(f"User '{current_user.username}' triggering AI review for Act ID: {db_act.id}")

    # --- Dynamic Model Selection Logic ---
    model_config_to_use = None
    if payload.model_config_id and payload.model_config_id in model_cache.configurations:
        model_config_to_use = model_cache.configurations[payload.model_config_id]
    else:
        # Fallback: Find the first available JSON-enabled model
        for config in model_cache.generation_models.values():
            if config.is_json_mode:
                model_config_to_use = config
                break
    
    if not model_config_to_use:
        logger.error(f"AI Review for Act {db_act.id}: No suitable JSON-enabled AI model configuration found.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI review service is not configured for structured output.")
    
    review_act_content_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("ReviewActContentEnhanced")
    if not review_act_content_function:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI content review service function is not configured.")

    logger.info(f"Using AI Model Config '{model_config_to_use.display_name}' (ID: {model_config_to_use.id}) for review.")
    
    # --- Build context for AI prompt ---
    from app.crud import story as crud_story, act as crud_act
    
    # Get story context
    if not db_act.story:
        story_obj = await crud_story.get_story_for_user(db, story_id=db_act.story_id, user_id=current_user.id)
        if not story_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent story not found or not accessible.")
    else:
        story_obj = db_act.story

    story_title_ctx = story_obj.title or "Untitled Story"
    story_summary_ctx = story_obj.short_description or "No story summary provided."
    story_class_ctx = db_act.story_class.description if db_act.story_class and db_act.story_class.description else "Default writing style."
    
    # Get previous acts context
    previous_acts = await crud_act.get_acts_by_story(db, story_id=story_obj.id)
    previous_acts_filtered = [act for act in previous_acts if act.act_number < db_act.act_number]
    
    if previous_acts_filtered:
        prev_summaries = []
        for prev_act in sorted(previous_acts_filtered, key=lambda a: a.act_number):
            summary = prev_act.act_summary or "No summary available."
            prev_summaries.append(f"Act {prev_act.act_number}: {prev_act.title} - {summary}")
        summaries_of_previous_acts_ctx = "\n".join(prev_summaries)
    else:
        summaries_of_previous_acts_ctx = "This is the first act."
    
    # Get linked world elements context
    linked_chars = await crud_character.get_characters_for_story(db, story_id=story_obj.id)
    linked_locs = await crud_location.get_locations_for_story(db, story_id=story_obj.id)
    linked_lore = await crud_lore_item.get_lore_items_for_story(db, story_id=story_obj.id)
    
    linked_characters_context_str = _format_linked_elements_for_prompt(linked_chars, "Character", "name", "role_in_story")
    linked_locations_context_str = _format_linked_elements_for_prompt(linked_locs, "Location", "name", "significance_to_story")
    linked_lore_items_context_str = _format_linked_elements_for_prompt(linked_lore, "Lore Item", "title", "relevance_to_story")
    
    # Get content to analyze
    act_content_to_analyze = payload.act_content_to_analyze_override or db_act.description or ""
    act_content_for_ai = convert_html_to_markdown(act_content_to_analyze)
    
    if not act_content_for_ai.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No act content available for review.")

    # --- Create execution settings ---
    exec_settings = OpenAIChatPromptExecutionSettings(
        service_id=model_config_to_use.model_name,
        max_tokens=model_config_to_use.max_tokens,
        temperature=model_config_to_use.temperature,
        top_p=model_config_to_use.top_p,
        presence_penalty=model_config_to_use.presence_penalty,
        frequency_penalty=model_config_to_use.frequency_penalty,
        response_format={"type": "json_object"}  # Review function always needs JSON
    )
    
    kernel_args = KernelArguments(
        settings=exec_settings,
        story_title=story_title_ctx,
        story_summary=story_summary_ctx,
        act_number=str(db_act.act_number),
        act_title=db_act.title or "Untitled Act",
        act_summary=db_act.act_summary or "No summary provided.",
        act_content_to_analyze=act_content_for_ai,
        summaries_of_previous_acts=summaries_of_previous_acts_ctx,
        story_class_context=story_class_ctx,
        linked_characters_context=linked_characters_context_str,
        linked_locations_context=linked_locations_context_str,
        linked_lore_items_context=linked_lore_items_context_str
    )

    raw_llm_output_str = "" 
    try:
        start_time = time.perf_counter()
        sk_result: FunctionResult = await kernel.invoke(review_act_content_function, arguments=kernel_args)
        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)

        # Get the raw response FIRST, before trying to get usage data
        raw_llm_output_str = str(sk_result.value[0]) if sk_result.value else ""
        logger.debug(f"AI Review raw response for Act {db_act.id}: {raw_llm_output_str[:200]}...")

        usage_data = get_usage_from_sk_result(sk_result)
        logger.info(f"AI Review for Act {db_act.id}: Usage data extracted: {usage_data}")
        
        if usage_data:
            logger.info(f"AI Review for Act {db_act.id}: Logging AI call with usage data - Prompt: {usage_data.get('prompt_tokens', 0)}, Completion: {usage_data.get('completion_tokens', 0)}, Total: {usage_data.get('total_tokens', 0)}")
            await log_ai_call(
                user_id=current_user.id,
                model_config=model_config_to_use,
                usage=usage_data,
                call_type="act_review",
                input_prompt=act_content_for_ai,
                duration_ms=duration_ms,
                object_id=db_act.id
            )
            logger.info(f"AI Review for Act {db_act.id}: Cost logging completed successfully.")
        else:
            logger.warning(f"AI Review for Act {db_act.id}: No usage data available from semantic kernel result. Attempting token estimation for cost logging.")
            # Fall back to token estimation for cost logging
            from app.services.cost_tracker_service import estimate_tokens_for_streaming_call
            try:
                estimated_usage = estimate_tokens_for_streaming_call(
                    input_text=act_content_for_ai,
                    output_text=raw_llm_output_str,  # Now this will have the actual output
                    model_name=model_config_to_use.model_name
                )
                logger.info(f"AI Review for Act {db_act.id}: Estimated usage - Prompt: {estimated_usage.get('prompt_tokens', 0)}, Completion: {estimated_usage.get('completion_tokens', 0)}, Total: {estimated_usage.get('total_tokens', 0)}")
                
                await log_ai_call(
                    user_id=current_user.id,
                    model_config=model_config_to_use,
                    usage=estimated_usage,
                    call_type="act_review",
                    input_prompt=act_content_for_ai,
                    duration_ms=duration_ms,
                    object_id=db_act.id
                )
                logger.info(f"AI Review for Act {db_act.id}: Cost logging completed with estimated tokens.")
            except Exception as e:
                logger.error(f"AI Review for Act {db_act.id}: Failed to estimate tokens and log cost: {e}", exc_info=True)
        logger.debug(f"AI Review raw response for Act {db_act.id}: {raw_llm_output_str[:200]}...")
        
        if not raw_llm_output_str.strip():
            logger.error(f"AI Review for Act {db_act.id}: Empty response from AI service.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI service returned empty response.")
        
        # Parse JSON response
        try:
            ai_response_json = json.loads(raw_llm_output_str)
        except json.JSONDecodeError as e:
            logger.error(f"AI Review for Act {db_act.id}: Failed to parse JSON response: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI returned improperly formatted data.")
        
        # Clean up AI response for validation
        def clean_rating_field(obj, field_path):
            """Convert string ratings like 'N/A - no dialogue' to null for optional metrics"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "rating" and isinstance(value, str) and ("N/A" in value or "n/a" in value.lower()):
                        obj[key] = None
                    elif isinstance(value, (dict, list)):
                        clean_rating_field(value, f"{field_path}.{key}")
            elif isinstance(obj, list):
                for item in obj:
                    clean_rating_field(item, field_path)
        
        # Clean the metrics section
        if "metrics" in ai_response_json:
            clean_rating_field(ai_response_json["metrics"], "metrics")
        
        # Validate and create response object
        try:
            response = ActAIReviewResponse.model_validate(ai_response_json)
            logger.info(f"AI Review for Act {db_act.id}: Successfully parsed {len(response.suggestions)} suggestions and metrics.")
            return response
        except Exception as e:
            logger.error(f"AI Review for Act {db_act.id}: Failed to validate response schema: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI returned improperly formatted data.")
        
    except APIError as e_api:
        logger.error(f"OpenAI API error during Act {db_act.id} review: {e_api}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service temporarily unavailable.")
    except Exception as e_sk: 
        logger.error(f"Error invoking SK for AI review of Act {db_act.id}: {e_sk}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing AI review request.")

