# /ai_rag_story_app/app/processing/world_element_processor.py

import logging
import re 
import asyncio
from typing import Any, Optional

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from semantic_kernel.exceptions import ServiceResponseException, KernelInvokeException, FunctionExecutionException

from app.db.database import async_session_local
from app.models.uploaded_document import SourceElementTypeEnum
from app.schemas.document import UploadedDocumentCreate, DocumentStatus
from app.crud import character as crud_character
from app.crud import location as crud_location
from app.crud import lore_item as crud_lore_item
from app.crud import document as crud_document_db 
from app.services.sk_kernel_instance import (
    kernel, 
    convert_character_to_rag_text_function, 
    convert_location_to_rag_text_function,
    convert_lore_item_to_rag_text_function
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

from app.processing.rag_ingestion import process_generated_text_for_rag
from app.services.azure_ai_search_service import AzureAISearchService
from app.core.config import settings
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result, estimate_tokens_for_streaming_call
from app.services.ai_model_cache import model_cache
import time

logger = logging.getLogger(__name__)

def _sanitize_filename_for_rag(name: str, prefix: str, element_id: int) -> str:
    if not name: name = "untitled"
    sanitized_name = re.sub(r'[^\w\s-]', '', name).strip()
    sanitized_name = re.sub(r'[-\s]+', '-', sanitized_name)
    return f"{prefix}_{element_id}_{sanitized_name[:50]}_rag_gen.txt"

def _extract_delimited_text(text_with_delimiters: Optional[str], element_type_upper_for_delimiter: str) -> str:
    if not text_with_delimiters:
        logger.warning(f"No text provided to _extract_delimited_text for {element_type_upper_for_delimiter}.")
        return ""
    start_delimiter = f"[START_{element_type_upper_for_delimiter}_RAG_TEXT]"
    end_delimiter = f"[END_{element_type_upper_for_delimiter}_RAG_TEXT]"
    start_idx = text_with_delimiters.find(start_delimiter)
    end_idx = text_with_delimiters.find(end_delimiter)
    rag_text = ""
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        rag_text = text_with_delimiters[start_idx + len(start_delimiter):end_idx].strip()
    else:
        logger.warning(f"Delimiters {start_delimiter}/{end_delimiter} not found for {element_type_upper_for_delimiter}. Using full output.")
        rag_text = text_with_delimiters.strip()
    return rag_text

async def generate_and_index_world_element_rag_text_task(
    element_type_str: str, 
    element_id: int, 
    user_id: int, 
    world_id: int,
    background_tasks: BackgroundTasks,
    model_config_id: Optional[int] = None
):
    logger.info(f"RAG GEN TASK: Starting for {element_type_str} ID: {element_id}")
    search_service_instance: Optional[AzureAISearchService] = None
    if settings.AZURE_AI_SEARCH_ENDPOINT and settings.AZURE_AI_SEARCH_API_KEY:
        search_service_instance = AzureAISearchService(endpoint=str(settings.AZURE_AI_SEARCH_ENDPOINT), api_key=settings.AZURE_AI_SEARCH_API_KEY, index_name=settings.AZURE_AI_SEARCH_INDEX_NAME)
    
    db_document_record_id_for_error_status: Optional[int] = None
    
    async with async_session_local() as db:
        try:
            element_data: Any = None
            sk_function: Any = None
            source_element_type_enum_member: Optional[SourceElementTypeEnum] = None
            element_name_for_file: str = "unknown_element"
            input_args = KernelArguments()

            if element_type_str == "character":
                element_data = await crud_character.get_character(db, character_id=element_id)
                if element_data:
                    sk_function, source_element_type_enum_member, element_name_for_file = convert_character_to_rag_text_function, SourceElementTypeEnum.CHARACTER_LORE, element_data.name
                    input_args.update(
                        character_name=element_data.name, 
                        character_description=element_data.description or "N/A", 
                        character_age_category=element_data.age_category or "N/A",
                        character_profession=element_data.profession or "N/A",
                        character_personality_traits=element_data.personality_traits or "N/A", 
                        character_core_motivations=", ".join(element_data.core_motivations) if element_data.core_motivations and isinstance(element_data.core_motivations, list) else (element_data.core_motivations or "N/A"),
                        character_backstory=element_data.backstory or "N/A",
                        character_short_backstory=element_data.short_backstory or "N/A",
                        character_next_quest_scenario=element_data.next_quest_scenario or "N/A",
                        character_first_meeting_message=element_data.first_meeting_message or "N/A",
                        character_visual_prompt=element_data.visual_prompt or "N/A",
                        character_relationships=element_data.relationships or "N/A",
                        character_image_prompt_definition=element_data.image_prompt_definition or "N/A"
                    )
            elif element_type_str == "location":
                element_data = await crud_location.get_location(db, location_id=element_id)
                if element_data:
                    sk_function, source_element_type_enum_member, element_name_for_file = convert_location_to_rag_text_function, SourceElementTypeEnum.LOCATION_LORE, element_data.name
                    input_args.update(
                        location_name=element_data.name, 
                        location_description=element_data.description or "N/A", 
                        location_atmosphere=element_data.atmosphere or "N/A", 
                        location_scale=element_data.scale.value if element_data.scale else "N/A",
                        location_geography=element_data.geography or "N/A",
                        location_cultural_context=element_data.cultural_context or "N/A",
                        location_significance=element_data.significance or "N/A",
                        location_connected_elements=element_data.connected_elements or "N/A",
                        location_image_prompt_definition=element_data.image_prompt_definition or "N/A"
                    )
            elif element_type_str == "lore_item":
                element_data = await crud_lore_item.get_lore_item(db, lore_item_id=element_id)
                if element_data:
                    sk_function, source_element_type_enum_member, element_name_for_file = convert_lore_item_to_rag_text_function, SourceElementTypeEnum.LORE_ITEM_LORE, element_data.title
                    input_args.update(
                        lore_item_title=element_data.title, 
                        lore_item_category=element_data.category.value if element_data.category else "N/A", 
                        lore_item_description=element_data.description or "N/A",
                        lore_item_related_elements=element_data.related_elements or "N/A",
                        lore_item_image_prompt_definition=element_data.image_prompt_definition or "N/A"
                    )

            if not all([element_data, sk_function, source_element_type_enum_member]):
                raise ValueError(f"Could not prepare RAG generation for {element_type_str} ID {element_id}")

            # Determine which model to use for RAG generation
            rag_model_config = None
            if model_config_id and model_config_id in model_cache.configurations:
                rag_model_config = model_cache.configurations[model_config_id]
                logger.info(f"RAG GEN TASK: Using selected model '{rag_model_config.display_name}' for {element_type_str} ID {element_id}")
            else:
                rag_model_config = model_cache.default_generation_model
                if rag_model_config:
                    logger.info(f"RAG GEN TASK: Using default model '{rag_model_config.display_name}' for {element_type_str} ID {element_id}")
                elif model_cache.generation_models:
                    rag_model_config = next(iter(model_cache.generation_models.values()))
                    logger.info(f"RAG GEN TASK: Using fallback model '{rag_model_config.display_name}' for {element_type_str} ID {element_id}")

            # Create execution settings for the selected model
            if rag_model_config:
                exec_settings = AzureChatPromptExecutionSettings(
                    service_id=rag_model_config.model_name,
                    max_tokens=rag_model_config.max_tokens,
                    temperature=rag_model_config.temperature,
                    top_p=rag_model_config.top_p,
                    presence_penalty=rag_model_config.presence_penalty,
                    frequency_penalty=rag_model_config.frequency_penalty
                )
                input_args.update(settings=exec_settings)
                logger.debug(f"RAG GEN TASK: Created execution settings for model '{rag_model_config.model_name}' for {element_type_str} ID {element_id}")

            # Execute the AI call with retry logic for rate limiting
            max_retries = 3
            base_delay = 60  # Start with 60 seconds as suggested by Azure error message
            
            for attempt in range(max_retries + 1):
                try:
                    start_time = time.perf_counter()
                    sk_result = await kernel.invoke(sk_function, arguments=input_args)
                    end_time = time.perf_counter()
                    duration_ms = int((end_time - start_time) * 1000)
                    break  # Success, exit retry loop
                    
                except (KernelInvokeException, FunctionExecutionException, ServiceResponseException) as e:
                    # Check if it's a rate limit error (429)
                    if "429" in str(e) and attempt < max_retries:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"RAG GEN TASK: Rate limit hit for {element_type_str} ID {element_id}, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Re-raise if not rate limit or max retries exceeded
                        logger.error(f"RAG GEN TASK: AI call failed for {element_type_str} ID {element_id} after {attempt + 1} attempts: {e}")
                        raise
                except Exception as e:
                    logger.error(f"RAG GEN TASK: Unexpected error in AI call for {element_type_str} ID {element_id}: {e}")
                    raise
            
            # Log AI call for cost tracking
            try:
                raw_llm_output_str = str(sk_result)
                usage_data = get_usage_from_sk_result(sk_result)
                logger.info(f"RAG GEN TASK: Usage data extracted for {element_type_str} ID {element_id}: {usage_data}")
                
                # Use the same model configuration that was used for RAG generation
                model_config_to_use = rag_model_config
                
                if model_config_to_use:
                    if usage_data:
                        await log_ai_call(
                            user_id=user_id,
                            model_config=model_config_to_use,
                            usage=usage_data,
                            call_type=f"rag_text_generation_{element_type_str}",
                            input_prompt=f"{element_type_str.title()}: {element_name_for_file}",
                            duration_ms=duration_ms,
                            object_id=element_id
                        )
                        logger.info(f"RAG GEN TASK: Cost logging completed for {element_type_str} ID {element_id}.")
                    else:
                        # Estimate tokens for cost logging
                        input_text = f"{element_type_str.title()}: {element_name_for_file}"
                        estimated_usage = estimate_tokens_for_streaming_call(
                            input_text=input_text,
                            output_text=raw_llm_output_str,
                            model_name=model_config_to_use.model_name
                        )
                        
                        await log_ai_call(
                            user_id=user_id,
                            model_config=model_config_to_use,
                            usage=estimated_usage,
                            call_type=f"rag_text_generation_{element_type_str}",
                            input_prompt=input_text,
                            duration_ms=duration_ms,
                            object_id=element_id,
                            db=db  # Pass existing database session to prevent connection pool exhaustion
                        )
                        logger.info(f"RAG GEN TASK: Cost logging with estimation completed for {element_type_str} ID {element_id}.")
                else:
                    logger.warning(f"RAG GEN TASK: No model configuration available for cost logging for {element_type_str} ID {element_id}.")
            except Exception as cost_log_error:
                logger.error(f"RAG GEN TASK: Failed to log AI call cost for {element_type_str} ID {element_id}: {cost_log_error}", exc_info=True)
            rag_text = _extract_delimited_text(str(sk_result), element_type_str.upper())
            if not rag_text: return

            if search_service_instance:
                await search_service_instance.delete_documents_by_filter_async(f"source_element_id eq '{element_id}' and element_type eq '{source_element_type_enum_member.value}'")
            await crud_document_db.delete_generated_document_records(db, source_element_type_enum_member, element_id, world_id, user_id, BackgroundTasks())
            
            final_rag_filename = _sanitize_filename_for_rag(element_name_for_file, element_type_str, element_id)
            blob_path = f"generated_world_elements/{element_type_str}/{world_id}/{element_id}/{final_rag_filename}"
            doc_payload = UploadedDocumentCreate(
                filename=final_rag_filename, content_type="text/plain", blob_storage_path=blob_path,
                status=DocumentStatus.UPLOADED, user_id=user_id, world_id=world_id,
                source_element_type=source_element_type_enum_member,
                **{f"source_{element_type_str}_id": element_id}
            )
            db_doc = await crud_document_db.create_document_record_from_schema(db, doc_payload)
            db_document_record_id_for_error_status = db_doc.id

            await process_generated_text_for_rag(
                db, db_doc.id, rag_text, final_rag_filename, blob_path,
                user_id, world_id, source_element_type_enum_member.value, str(element_id)
            )
        except Exception as e:
            logger.error(f"RAG GEN TASK: Error processing {element_type_str} ID {element_id}: {e}", exc_info=True)
            if db_document_record_id_for_error_status:
                await crud_document_db.update_document_status(db, db_document_record_id_for_error_status, DocumentStatus.ERROR, f"RAG Gen Task Error: {str(e)[:250]}")
        finally:
            if search_service_instance: await search_service_instance.close_async_clients()