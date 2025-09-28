# /ai_rag_story_app/app/processing/importer_jobs.py
import logging
import json
import asyncio
import shutil
import os
import uuid
import time
from typing import Optional

from fastapi import BackgroundTasks
from app.db.database import async_session_local
from app.models.world import World
from app.schemas.world import WorldCreate
from app.schemas.character import CharacterCreate
from app.schemas.location import LocationCreate
from app.schemas.lore_item import LoreItemCreate, LoreItemCategoryEnum
from app.crud import world as crud_world, character as crud_character, location as crud_location, lore_item as crud_lore_item
from app.crud import job_status as crud_job_status
from app.models.job_status import JobStateEnum
from app.processing.text_extraction import extract_text_from_file_path
from app.processing.world_element_processor import generate_and_index_world_element_rag_text_task
from app.core.config import settings

# --- New imports for dynamic model handling ---
from app.services.ai_model_cache import model_cache
from app.services.sk_kernel_instance import kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.exceptions import KernelInvokeException, FunctionExecutionException, ServiceResponseException
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result, estimate_tokens_for_streaming_call
from app.services.ai_client_factory import AIClientFactory
from app.models.ai_model_config import AIProviderEnum
import openai
from app.schemas.document import UploadedDocumentCreate
from app.models.uploaded_document import SourceElementTypeEnum
from app.crud import document as crud_document
from app.processing.rag_ingestion import process_uploaded_document_task
import time

logger = logging.getLogger(__name__)

def _load_extraction_prompt() -> str:
    """Load the world extraction prompt from file."""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_file = os.path.join(current_dir, '..', 'prompts', 'system', 'extract_world_elements_from_text.txt')
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # Remove the <message role="system"> wrapper if present
        if content.startswith('<message role="system">'):
            content = content.replace('<message role="system">', '').replace('</message>', '').strip()
        return content
    except Exception as e:
        logger.error(f"Failed to load extraction prompt: {e}")
        raise RuntimeError(f"Could not load extraction prompt: {e}")

async def _call_ai_for_world_extraction(model_config, prompt_text, input_text, job_id):
    """
    Call AI for world extraction using either Semantic Kernel (Azure) or direct API (OpenRouter).
    Forces JSON mode for structured extraction.
    
    Args:
        model_config: AI model configuration
        prompt_text: System prompt for extraction
        input_text: Text to extract from (book title or document content)
        job_id: Job ID for logging
        
    Returns:
        tuple: (ai_response_text, usage_data, duration_ms)
    """
    start_time = time.perf_counter()
    
    if model_config.provider == AIProviderEnum.AZURE:
        # Use Semantic Kernel for Azure OpenAI
        logger.info(f"JOB_ID: {job_id} - Using Semantic Kernel approach for Azure model: {model_config.display_name}")
        
        extract_world_elements_from_text_function = kernel.plugins.get("WorldGenerationPlugin", {}).get("ExtractWorldElementsFromText")
        if not extract_world_elements_from_text_function:
            raise RuntimeError("ExtractWorldElementsFromText function not available in Semantic Kernel")
        
        exec_settings = AzureChatPromptExecutionSettings(
            service_id="azure_openai_chat_service",
            max_tokens=model_config.max_tokens,
            temperature=model_config.temperature,
            response_format={"type": "json_object"}
        )
        kernel_args = KernelArguments(settings=exec_settings, document_full_text=input_text)
        
        sk_result = await kernel.invoke(extract_world_elements_from_text_function, arguments=kernel_args)
        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)
        
        usage_data = get_usage_from_sk_result(sk_result)
        return str(sk_result), usage_data, duration_ms
        
    elif model_config.provider in [AIProviderEnum.OPENROUTER, AIProviderEnum.OPENAI]:
        # Use direct API call for OpenRouter/OpenAI
        logger.info(f"JOB_ID: {job_id} - Using direct API approach for {model_config.provider} model: {model_config.display_name}")
        
        try:
            client = AIClientFactory.create_client_for_model(model_config)
        except ValueError as e:
            raise RuntimeError(f"Failed to create {model_config.provider} client: {e}. Please check your API key configuration.")
        
        model_name = AIClientFactory.resolve_model_name(model_config)
        
        messages = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": f"Please analyze the following document content and extract the world-building elements into the specified JSON format.\n\nDOCUMENT CONTENT:\n{input_text}"}
        ]
        
        logger.info(f"JOB_ID: {job_id} - Calling {model_config.provider} API with model: {model_name}")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=model_config.max_tokens,
            temperature=model_config.temperature,
            response_format={"type": "json_object"} if model_config.is_json_mode else None
        )
        
        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)
        
        # Extract usage data
        usage_data = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0
        }
        
        return response.choices[0].message.content, usage_data, duration_ms
        
    else:
        raise ValueError(f"Unsupported AI provider: {model_config.provider}")

async def _call_ai_for_text_generation(model_config, prompt_text, input_text, job_id):
    """
    Call AI for narrative text generation using either Semantic Kernel (Azure) or direct API (OpenRouter).
    Does NOT force JSON mode - used for generating narrative descriptions.
    
    Args:
        model_config: AI model configuration
        prompt_text: System prompt for text generation
        input_text: Input context for generation
        job_id: Job ID for logging
        
    Returns:
        tuple: (ai_response_text, usage_data, duration_ms)
    """
    start_time = time.perf_counter()
    
    if model_config.provider == AIProviderEnum.AZURE:
        # Use Semantic Kernel for Azure OpenAI
        logger.info(f"JOB_ID: {job_id} - Using Semantic Kernel approach for Azure text generation: {model_config.display_name}")
        
        # Note: We'll use direct API instead of SK for text generation to avoid JSON mode enforcement
        # Fall through to the OpenRouter/OpenAI path which works for Azure too
        pass
        
    if model_config.provider in [AIProviderEnum.OPENROUTER, AIProviderEnum.OPENAI, AIProviderEnum.AZURE]:
        # Use direct API call for text generation (no JSON mode)
        logger.info(f"JOB_ID: {job_id} - Using direct API approach for {model_config.provider} text generation: {model_config.display_name}")
        
        try:
            client = AIClientFactory.create_client_for_model(model_config)
        except ValueError as e:
            raise RuntimeError(f"Failed to create {model_config.provider} client: {e}. Please check your API key configuration.")
        
        model_name = AIClientFactory.resolve_model_name(model_config)
        
        messages = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": input_text}
        ]
        
        logger.info(f"JOB_ID: {job_id} - Calling {model_config.provider} API for text generation with model: {model_name}")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=model_config.max_tokens,
            temperature=model_config.temperature,
            # No response_format for text generation - let it generate natural text
        )
        
        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)
        
        # Extract usage data
        usage_data = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0
        }
        
        return response.choices[0].message.content, usage_data, duration_ms
        
    else:
        raise ValueError(f"Unsupported AI provider: {model_config.provider}")

def _find_best_json_model(preferred_model_config=None):
    """
    Find the best JSON-enabled model for world imports.
    If a preferred model is provided, use it even if not explicitly marked as JSON-enabled 
    (most modern models can handle JSON output).
    Otherwise, prefers the default model if it supports JSON mode, or picks the first available JSON model.
    """
    # If a preferred model is specified, try to use it first
    if preferred_model_config:
        logger.info(f"Using user-selected model '{preferred_model_config.display_name}' for import (JSON mode: {preferred_model_config.is_json_mode})")
        return preferred_model_config
    
    # First, check if the default model supports JSON mode
    default_model = model_cache.default_generation_model
    if default_model and default_model.is_json_mode:
        return default_model
    
    # Fall back to any JSON-enabled model
    return next((c for c in model_cache.generation_models.values() if c.is_json_mode), None)

async def import_world_from_book_task(job_id: str, book_title: str, user_id: int, model_config_id: Optional[int] = None):
    logger.info(f"JOB_ID: {job_id} - Starting world import for book: '{book_title}'")
    created_world_id: Optional[int] = None
    created_world_name: Optional[str] = None
    
    try:
        # --- Select a suitable model for world generation ---
        selected_model_name = None
        model_fallback_occurred = False
        
        if model_config_id and model_config_id in model_cache.configurations:
            selected_model = model_cache.configurations[model_config_id]
            selected_model_name = selected_model.display_name
            
            # Use the selected model regardless of JSON mode flag (most modern models can handle JSON)
            world_gen_model_config = _find_best_json_model(preferred_model_config=selected_model)
            model_fallback_occurred = False  # No fallback needed since we're using user selection
        else:
            # No specific model selected, find the best JSON-enabled model for this task.
            world_gen_model_config = _find_best_json_model()
        
        if not world_gen_model_config:
            raise RuntimeError("No suitable JSON-enabled AI model configuration found for world generation.")
        
        logger.info(f"JOB_ID: {job_id} - Using AI model '{world_gen_model_config.display_name}' for world generation.")
        
        generate_world_from_book_function = kernel.plugins.get("WorldGenerationPlugin", {}).get("GenerateWorldFromBookTitle")
        if not generate_world_from_book_function: 
            raise RuntimeError("World generation SK function not available.")
        
        async with async_session_local() as db:
            # Create user-friendly status message
            status_msg = f"Using {world_gen_model_config.display_name} to generate world structure..."
            
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, status_msg)

            # --- Dynamically create execution settings ---
            exec_settings = AzureChatPromptExecutionSettings(
                service_id="azure_openai_chat_service",  # Use the static service ID from kernel
                max_tokens=world_gen_model_config.max_tokens,
                temperature=world_gen_model_config.temperature,
                response_format={"type": "json_object"}
            )
            kernel_args = KernelArguments(
                settings=exec_settings,
                book_title=book_title, 
                MAX_ELEMENTS_PER_TYPE=str(settings.MAX_ELEMENTS_PER_TYPE_FROM_BOOK_IMPORT)
            )

            # Execute AI call with retry logic for rate limiting
            max_retries = 3
            base_delay = 60  # Start with 60 seconds as suggested by Azure error message
            
            for attempt in range(max_retries + 1):
                try:
                    start_time = time.perf_counter()
                    sk_result = await kernel.invoke(generate_world_from_book_function, arguments=kernel_args)
                    end_time = time.perf_counter()
                    duration_ms = int((end_time - start_time) * 1000)
                    break  # Success, exit retry loop
                    
                except (KernelInvokeException, FunctionExecutionException, ServiceResponseException, Exception) as e:
                    # Check if it's a rate limit error (429)
                    if "429" in str(e) and attempt < max_retries:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"JOB_ID: {job_id} - Rate limit hit for world generation, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, f"Rate limit reached, retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Re-raise if not rate limit or max retries exceeded
                        logger.error(f"JOB_ID: {job_id} - World generation failed after {attempt + 1} attempts: {e}")
                        raise
            
            # Log AI call for cost tracking
            raw_llm_output_str = str(sk_result)
            usage_data = get_usage_from_sk_result(sk_result)
            logger.info(f"JOB_ID: {job_id} - Usage data extracted from book import: {usage_data}")
            
            if usage_data:
                logger.info(f"JOB_ID: {job_id} - Logging AI call with usage data - Prompt: {usage_data.get('prompt_tokens', 0)}, Completion: {usage_data.get('completion_tokens', 0)}, Total: {usage_data.get('total_tokens', 0)}")
                await log_ai_call(
                    user_id=user_id,
                    model_config=world_gen_model_config,
                    usage=usage_data,
                    call_type="world_import_from_book",
                    input_prompt=f"Book Title: {book_title}",
                    duration_ms=duration_ms,
                    job_id=job_id,
                    db=db
                )
                logger.info(f"JOB_ID: {job_id} - Cost logging completed successfully.")
            else:
                logger.warning(f"JOB_ID: {job_id} - No usage data available from semantic kernel result. Attempting token estimation for cost logging.")
                try:
                    estimated_usage = estimate_tokens_for_streaming_call(
                        input_text=f"Book Title: {book_title}",
                        output_text=raw_llm_output_str,
                        model_name=world_gen_model_config.model_name
                    )
                    logger.info(f"JOB_ID: {job_id} - Estimated usage - Prompt: {estimated_usage.get('prompt_tokens', 0)}, Completion: {estimated_usage.get('completion_tokens', 0)}, Total: {estimated_usage.get('total_tokens', 0)}")
                    
                    await log_ai_call(
                        user_id=user_id,
                        model_config=world_gen_model_config,
                        usage=estimated_usage,
                        call_type="world_import_from_book",
                        input_prompt=f"Book Title: {book_title}",
                        duration_ms=duration_ms,
                        job_id=job_id,
                        db=db
                    )
                    logger.info(f"JOB_ID: {job_id} - Cost logging with estimation completed successfully.")
                except Exception as cost_log_error:
                    logger.error(f"JOB_ID: {job_id} - Failed to log AI call cost: {cost_log_error}", exc_info=True)
            
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Saving new world...")
            
            # Debug logging for AI response
            ai_response_str = str(sk_result)
            logger.info(f"JOB_ID {job_id}: AI Response length: {len(ai_response_str)} characters")
            logger.info(f"JOB_ID {job_id}: AI Response preview (first 500 chars): {ai_response_str[:500]}")
            
            world_data = json.loads(ai_response_str)["world"]
            world_schema = WorldCreate(name=world_data.get("name", book_title), description=world_data.get("description", f"World from '{book_title}'"))
            created_world = await crud_world.create_world(db, world_in=world_schema, user_id=user_id)
            await db.commit()
            await db.refresh(created_world)
            created_world_id = created_world.id
            created_world_name = created_world.name

            json_data = json.loads(ai_response_str)
            dummy_bg_tasks = BackgroundTasks()
            
            # Debug logging for JSON structure
            logger.info(f"JOB_ID {job_id}: AI Response JSON keys: {list(json_data.keys())}")
            
            # Check if this is nested or direct structure
            if "world" in json_data and "characters" in json_data["world"]:
                logger.info(f"JOB_ID {job_id}: Detected nested structure - characters are under 'world' key")
                characters_data = json_data["world"].get("characters", [])
                locations_data = json_data["world"].get("locations", [])
                lore_data = json_data["world"].get("lore_items", [])
            else:
                logger.info(f"JOB_ID {job_id}: Using flat structure - characters at root level")
                characters_data = json_data.get("characters", [])
                locations_data = json_data.get("locations", [])
                lore_data = json_data.get("lore_items", [])
            
            logger.info(f"JOB_ID {job_id}: Found {len(characters_data)} characters, {len(locations_data)} locations, {len(lore_data)} lore items in AI response")
            
            # Log first character for debugging if available
            if characters_data:
                logger.info(f"JOB_ID {job_id}: First character data sample: {characters_data[0]}")
                # Validate the first character against schema
                try:
                    test_char = CharacterCreate(**characters_data[0])
                    logger.info(f"JOB_ID {job_id}: Character schema validation passed for first character")
                except Exception as schema_error:
                    logger.error(f"JOB_ID {job_id}: Character schema validation failed for first character: {schema_error}")
            else:
                logger.warning(f"JOB_ID {job_id}: No characters found in AI response!")
                # Log the full JSON structure for debugging
                logger.warning(f"JOB_ID {job_id}: Full JSON structure: {json.dumps(json_data, indent=2)[:1000]}...")
            
            for i, char_data in enumerate(characters_data):
                try: 
                    logger.info(f"JOB_ID {job_id}: Creating character {i+1}/{len(characters_data)}: {char_data.get('name', 'UNNAMED')}")
                    character_obj = await crud_character.create_character(db, CharacterCreate(**char_data), created_world_id, user_id, dummy_bg_tasks, world_gen_model_config.id if world_gen_model_config else None)
                    logger.info(f"JOB_ID {job_id}: Successfully created character '{char_data.get('name')}' with database ID: {character_obj.id}")
                except Exception as e: 
                    logger.error(f"JOB_ID {job_id}: Failed to create character '{char_data.get('name')}': {e}", exc_info=True)
                    
            for i, loc_data in enumerate(locations_data):
                try:
                    # Handle invalid scale values for backwards compatibility
                    from app.schemas.location import LocationScaleEnum
                    valid_scales = [e.value for e in LocationScaleEnum]
                    current_scale = loc_data.get('scale')
                    if current_scale and current_scale not in valid_scales:
                        logger.warning(f"JOB_ID {job_id}: Converting invalid scale '{current_scale}' to 'OTHER' for location '{loc_data.get('name')}'")
                        loc_data['scale'] = 'OTHER'
                    
                    logger.info(f"JOB_ID {job_id}: Creating location {i+1}/{len(locations_data)}: {loc_data.get('name', 'UNNAMED')}")
                    location_obj = await crud_location.create_location(db, LocationCreate(**loc_data), created_world_id, user_id, dummy_bg_tasks, world_gen_model_config.id if world_gen_model_config else None)
                    logger.info(f"JOB_ID {job_id}: Successfully created location '{loc_data.get('name')}' with database ID: {location_obj.id}")
                except Exception as e: 
                    logger.error(f"JOB_ID {job_id}: Failed to create location '{loc_data.get('name')}': {e}", exc_info=True)
                    
            for lore_item_data in lore_data:
                try:
                    if lore_item_data.get("category") not in [e.value for e in LoreItemCategoryEnum]: 
                        lore_item_data["category"] = "OTHER_LORE"
                    lore_obj = await crud_lore_item.create_lore_item(db, LoreItemCreate(**lore_item_data), created_world_id, user_id, dummy_bg_tasks, world_gen_model_config.id if world_gen_model_config else None)
                    logger.info(f"JOB_ID {job_id}: Successfully created lore item '{lore_item_data.get('title')}' with database ID: {lore_obj.id}")
                except Exception as e: 
                    logger.error(f"JOB_ID {job_id}: Failed to create lore item '{lore_item_data.get('title')}': {e}", exc_info=True)
            try:
                await db.commit()
                logger.info(f"JOB_ID {job_id}: Successfully committed World ID {created_world_id} and its elements to the database.")
            except Exception as commit_error:
                logger.error(f"JOB_ID {job_id}: Failed to commit database transaction: {commit_error}", exc_info=True)
                await db.rollback()
                raise

        # Phase 2: Run RAG indexing tasks concurrently
        if created_world_id:
            async with async_session_local() as db:
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Loading world elements for indexing...")
                all_elements_db = await asyncio.gather(
                    crud_character.get_characters_by_world(db, created_world_id, limit=500),
                    crud_location.get_locations_by_world(db, created_world_id, limit=500),
                    crud_lore_item.get_lore_items_by_world(db, created_world_id, limit=500)
                )

            rag_tasks = []
            dummy_bg_tasks_for_rag = BackgroundTasks()
            # Pass the same model configuration used for world generation to RAG tasks
            selected_model_id = world_gen_model_config.id if world_gen_model_config else None
            logger.info(f"JOB_ID {job_id}: Using model ID {selected_model_id} for RAG text generation (same as world generation)")
            for char in all_elements_db[0]: rag_tasks.append(generate_and_index_world_element_rag_text_task("character", char.id, user_id, created_world_id, dummy_bg_tasks_for_rag, selected_model_id))
            for loc in all_elements_db[1]: rag_tasks.append(generate_and_index_world_element_rag_text_task("location", loc.id, user_id, created_world_id, dummy_bg_tasks_for_rag, selected_model_id))
            for lore in all_elements_db[2]: rag_tasks.append(generate_and_index_world_element_rag_text_task("lore_item", lore.id, user_id, created_world_id, dummy_bg_tasks_for_rag, selected_model_id))

            if rag_tasks:
                # Update status with the actual number of elements to index
                async with async_session_local() as status_db:
                    await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, f"Indexing {len(rag_tasks)} elements for search (processing sequentially to avoid rate limits)...")
                logger.info(f"JOB_ID {job_id}: Starting sequential RAG indexing for {len(rag_tasks)} elements to avoid rate limits.")
                successful_tasks = 0
                failed_tasks = 0
                
                # Process tasks sequentially with delay to avoid Azure rate limits
                for i, task in enumerate(rag_tasks):
                    try:
                        # Update status every 5 elements
                        if i % 5 == 0:
                            async with async_session_local() as status_db:
                                await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, f"Indexing element {i+1}/{len(rag_tasks)} for search...")
                        
                        # Add timeout to prevent hanging
                        await asyncio.wait_for(task, timeout=120.0)  # 2 minute timeout per task
                        successful_tasks += 1
                        logger.info(f"JOB_ID {job_id}: Completed RAG task {i+1}/{len(rag_tasks)}")
                        
                        # Add delay between AI calls to respect rate limits
                        if i < len(rag_tasks) - 1:  # Don't delay after the last task
                            await asyncio.sleep(5)  # 5 second delay between calls to be more conservative
                    except asyncio.TimeoutError:
                        failed_tasks += 1
                        logger.error(f"JOB_ID {job_id}: RAG task {i+1} timed out after 2 minutes")
                        # Continue with next task
                    except Exception as task_error:
                        failed_tasks += 1
                        logger.error(f"JOB_ID {job_id}: RAG task {i+1} failed: {task_error}", exc_info=True)
                        # Continue with next task even if one fails
                
                logger.info(f"JOB_ID {job_id}: Finished sequential RAG indexing. Success: {successful_tasks}, Failed: {failed_tasks}")
                
                # Update final status with results
                if failed_tasks > 0:
                    async with async_session_local() as status_db:
                        await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, f"RAG indexing completed with some failures: {successful_tasks} successful, {failed_tasks} failed")

            async with async_session_local() as db:
                result_msg = f"Successfully imported world '{created_world_name}' (ID: {created_world_id}) and its elements."
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.COMPLETED, "Import complete!", result_message=result_msg, world_id=created_world_id)
        else:
            raise ValueError("World was not created, cannot proceed to RAG indexing.")

    except Exception as e:
        error_message = f"Failed to import world: {str(e)[:400]}"
        logger.error(f"JOB_ID {job_id}: {error_message}", exc_info=True)
        if created_world_id:
            async with async_session_local() as cleanup_db:
                world_to_delete = await cleanup_db.get(World, created_world_id)
                if world_to_delete: await cleanup_db.delete(world_to_delete); await cleanup_db.commit()
                logger.info(f"JOB_ID {job_id}: Rolled back creation of World ID {created_world_id} due to error.")
        async with async_session_local() as error_db:
            await crud_job_status.update_job_status(error_db, job_id, JobStateEnum.FAILED, "Error during import.", result_message=error_message)

async def create_world_and_extract_elements_from_document_task(
    job_id: str,
    world_name: str,
    user_id: int,
    temp_file_path: str,
    original_filename: str,
    model_config_id: Optional[int] = None
):
    logger.info(f"JOB_ID: {job_id} - Starting entity extraction from '{original_filename}' for new world '{world_name}' by User ID: {user_id}")
    created_world_id = None
    document_record = None
    
    try:
        # --- Select a suitable model for world element extraction ---
        selected_model_name = None
        model_fallback_occurred = False
        
        # HARDCODED: Always use GPT-4.1 Mini (Next Generation) for document imports (model ID 9)
        hardcoded_model_id = 9  # GPT-4.1 Mini (Next Generation)
        
        if hardcoded_model_id in model_cache.configurations:
            extraction_model_config = model_cache.configurations[hardcoded_model_id]
            selected_model_name = extraction_model_config.display_name
            logger.info(f"JOB_ID: {job_id} - HARDCODED: Using GPT-4.1 Mini (model ID {hardcoded_model_id}) for document import")
            model_fallback_occurred = False
        else:
            # Don't fallback to other models - fail the job if GPT-4.1 Mini isn't available
            error_msg = f"HARDCODED model GPT-4.1 Mini (ID {hardcoded_model_id}) not found in model cache. Document import requires this specific model."
            logger.error(f"JOB_ID: {job_id} - {error_msg}")
            raise RuntimeError(error_msg)
        
        if not extraction_model_config:
            raise RuntimeError("No suitable JSON-enabled AI model configuration found for element extraction.")
        
        logger.info(f"JOB_ID: {job_id} - Using AI model '{extraction_model_config.display_name}' for element extraction.")

        extract_world_elements_from_text_function = kernel.plugins.get("WorldGenerationPlugin", {}).get("ExtractWorldElementsFromText")
        if not extract_world_elements_from_text_function: 
            raise RuntimeError("Entity extraction AI function is not available.")
        
        async with async_session_local() as db:
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Creating world...")
            world_create_schema = WorldCreate(name=world_name, description=f"World generated from document: {original_filename}")
            created_world = await crud_world.create_world(db, world_in=world_create_schema, user_id=user_id)
            await db.commit()
            await db.refresh(created_world)
            created_world_id = created_world.id
            
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Extracting text from document...", world_id=created_world_id)
            full_text = await extract_text_from_file_path(temp_file_path, original_filename)
            if not full_text: raise ValueError("No text could be extracted from the document.")
            
            # Handle large documents by truncating to fit model context limits
            # Estimate tokens conservatively (1 token ≈ 4 characters for English text)
            estimated_tokens = len(full_text) // 4
            max_input_tokens = 120000  # Conservative limit leaving room for prompt and output
            
            if estimated_tokens > max_input_tokens:
                # Take the first portion and last portion of the document to capture beginning and end
                target_chars = max_input_tokens * 4
                first_half_chars = target_chars // 2
                last_half_chars = target_chars - first_half_chars
                
                logger.warning(f"JOB_ID: {job_id} - Document too large ({estimated_tokens} estimated tokens). Truncating to fit context window.")
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, f"Document too large, using first {first_half_chars//1000}K and last {last_half_chars//1000}K characters...")
                
                truncated_text = full_text[:first_half_chars] + "\n\n[... MIDDLE CONTENT TRUNCATED ...]\n\n" + full_text[-last_half_chars:]
                full_text = truncated_text
                logger.info(f"JOB_ID: {job_id} - Truncated document to {len(full_text)} characters")

            # Create document record for document library and RAG processing
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Adding document to library...")
            
            # Generate blob storage path
            import mimetypes
            content_type = mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
            blob_path = f"user_{user_id}/world_{created_world_id}/{uuid.uuid4().hex}/{original_filename}"
            
            # Create document record
            document_create = UploadedDocumentCreate(
                filename=original_filename,
                content_type=content_type,
                blob_storage_path=blob_path,
                user_id=user_id,
                world_id=created_world_id,
                source_element_type=SourceElementTypeEnum.USER_UPLOADED
            )
            
            document_record = await crud_document.create_document_record_from_schema(db, document_create)
            logger.info(f"JOB_ID: {job_id} - Created document record ID: {document_record.id} for '{original_filename}'")

            # Create user-friendly status message
            status_msg = f"Using {extraction_model_config.display_name} to identify elements..."
            
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, status_msg)
            
            # Load the extraction prompt
            extraction_prompt = _load_extraction_prompt()
            
            # Execute AI call with retry logic for rate limiting
            max_retries = 3
            base_delay = 60  # Start with 60 seconds as suggested by Azure error message
            
            for attempt in range(max_retries + 1):
                try:
                    ai_response_str, usage_data, duration_ms = await _call_ai_for_world_extraction(
                        extraction_model_config, extraction_prompt, full_text, job_id
                    )
                    break  # Success, exit retry loop
                    
                except (KernelInvokeException, FunctionExecutionException, ServiceResponseException, openai.RateLimitError, openai.BadRequestError, Exception) as e:
                    # Check if it's a rate limit error (429)
                    if "429" in str(e) and attempt < max_retries:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"JOB_ID: {job_id} - Rate limit hit for element extraction, retrying in {delay} seconds (attempt {attempt + 1}/{max_retries + 1})")
                        await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, f"Rate limit reached, retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    elif "Invalid JWT" in str(e) or "token-invalid" in str(e):
                        logger.error(f"JOB_ID: {job_id} - OpenRouter authentication error: {e}")
                        raise RuntimeError("OpenRouter authentication failed. Please check your OPENROUTER_API_KEY environment variable.")
                    elif "maximum context length" in str(e) and "tokens" in str(e):
                        logger.error(f"JOB_ID: {job_id} - Context length error: {e}")
                        raise RuntimeError(f"Document is too large for the selected model. Please try with a smaller document or different model.")
                    else:
                        # Re-raise if not rate limit or max retries exceeded
                        logger.error(f"JOB_ID: {job_id} - Element extraction failed after {attempt + 1} attempts: {e}")
                        raise
            
            # Log AI call for cost tracking
            logger.info(f"JOB_ID: {job_id} - Usage data extracted from document import: {usage_data}")
            
            if usage_data:
                logger.info(f"JOB_ID: {job_id} - Logging AI call with usage data - Prompt: {usage_data.get('prompt_tokens', 0)}, Completion: {usage_data.get('completion_tokens', 0)}, Total: {usage_data.get('total_tokens', 0)}")
                await log_ai_call(
                    user_id=user_id,
                    model_config=extraction_model_config,
                    usage=usage_data,
                    call_type="world_import_from_document",
                    input_prompt=f"Document: {original_filename} (length: {len(full_text)} chars)",
                    duration_ms=duration_ms,
                    job_id=job_id,
                    db=db
                )
                logger.info(f"JOB_ID: {job_id} - Cost logging completed successfully.")
            else:
                logger.warning(f"JOB_ID: {job_id} - No usage data available from AI response. Attempting token estimation for cost logging.")
                try:
                    estimated_usage = estimate_tokens_for_streaming_call(
                        input_text=full_text,
                        output_text=ai_response_str,
                        model_name=extraction_model_config.model_name
                    )
                    logger.info(f"JOB_ID: {job_id} - Estimated usage - Prompt: {estimated_usage.get('prompt_tokens', 0)}, Completion: {estimated_usage.get('completion_tokens', 0)}, Total: {estimated_usage.get('total_tokens', 0)}")
                    
                    await log_ai_call(
                        user_id=user_id,
                        model_config=extraction_model_config,
                        usage=estimated_usage,
                        call_type="world_import_from_document",
                        input_prompt=f"Document: {original_filename} (length: {len(full_text)} chars)",
                        duration_ms=duration_ms,
                        job_id=job_id,
                        db=db
                    )
                    logger.info(f"JOB_ID: {job_id} - Cost logging with estimation completed successfully.")
                except Exception as cost_log_error:
                    logger.error(f"JOB_ID: {job_id} - Failed to log AI call cost: {cost_log_error}", exc_info=True)
            
            # Debug logging for AI response
            logger.info(f"JOB_ID {job_id}: Document extraction AI Response length: {len(ai_response_str)} characters")
            logger.info(f"JOB_ID {job_id}: Document extraction AI Response preview (first 500 chars): {ai_response_str[:500]}")
            
            extracted_data = json.loads(ai_response_str)
            
            # Debug logging for JSON structure
            logger.info(f"JOB_ID {job_id}: Document extraction AI Response JSON keys: {list(extracted_data.keys())}")
            
            # Check if this is nested or direct structure
            if "world" in extracted_data and "characters" in extracted_data["world"]:
                logger.info(f"JOB_ID {job_id}: Document extraction - Detected nested structure")
                characters_data = extracted_data["world"].get("characters", [])
                locations_data = extracted_data["world"].get("locations", [])
                lore_data = extracted_data["world"].get("lore_items", [])
            else:
                logger.info(f"JOB_ID {job_id}: Document extraction - Using flat structure")
                characters_data = extracted_data.get("characters", [])
                locations_data = extracted_data.get("locations", [])
                lore_data = extracted_data.get("lore_items", [])
                
            logger.info(f"JOB_ID {job_id}: Document extraction found {len(characters_data)} characters, {len(locations_data)} locations, {len(lore_data)} lore items in AI response")
            
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, f"AI found {len(characters_data)} chars, {len(locations_data)} locs, {len(lore_data)} lore. Saving...")
            
            # Log first character for debugging if available
            if characters_data:
                logger.info(f"JOB_ID {job_id}: Document extraction first character data sample: {characters_data[0]}")
                # Validate the first character against schema
                try:
                    test_char = CharacterCreate(**characters_data[0])
                    logger.info(f"JOB_ID {job_id}: Document extraction - Character schema validation passed")
                except Exception as schema_error:
                    logger.error(f"JOB_ID {job_id}: Document extraction - Character schema validation failed: {schema_error}")
            else:
                logger.warning(f"JOB_ID {job_id}: Document extraction - No characters found in AI response!")
                # Log the full JSON structure for debugging
                logger.warning(f"JOB_ID {job_id}: Document extraction - Full JSON structure: {json.dumps(extracted_data, indent=2)[:1000]}...")
            
            dummy_bg_tasks = BackgroundTasks()
            
            for i, char_data in enumerate(characters_data):
                try: 
                    logger.info(f"JOB_ID {job_id}: Creating character {i+1}/{len(characters_data)} from document: {char_data.get('name', 'UNNAMED')}")
                    character_obj = await crud_character.create_character(db, CharacterCreate(**char_data), created_world_id, user_id, dummy_bg_tasks, extraction_model_config.id if extraction_model_config else None)
                    logger.info(f"JOB_ID {job_id}: Successfully created character '{char_data.get('name')}' from document with database ID: {character_obj.id}")
                except Exception as e: 
                    logger.error(f"JOB_ID {job_id}: Failed to create character '{char_data.get('name')}' from document: {e}", exc_info=True)
                    
            for i, loc_data in enumerate(locations_data):
                try:
                    # Handle invalid scale values for backwards compatibility
                    from app.schemas.location import LocationScaleEnum
                    valid_scales = [e.value for e in LocationScaleEnum]
                    current_scale = loc_data.get('scale')
                    if current_scale and current_scale not in valid_scales:
                        logger.warning(f"JOB_ID {job_id}: Converting invalid scale '{current_scale}' to 'OTHER' for location '{loc_data.get('name')}'")
                        loc_data['scale'] = 'OTHER'
                    
                    logger.info(f"JOB_ID {job_id}: Creating location {i+1}/{len(locations_data)} from document: {loc_data.get('name', 'UNNAMED')}")
                    location_obj = await crud_location.create_location(db, LocationCreate(**loc_data), created_world_id, user_id, dummy_bg_tasks, extraction_model_config.id if extraction_model_config else None)
                    logger.info(f"JOB_ID {job_id}: Successfully created location '{loc_data.get('name')}' from document with database ID: {location_obj.id}")
                except Exception as e: 
                    logger.error(f"JOB_ID {job_id}: Failed to create location '{loc_data.get('name')}' from document: {e}", exc_info=True)
                    
            for lore_item_data in lore_data:
                try:
                    if lore_item_data.get("category") not in [e.value for e in LoreItemCategoryEnum]: 
                        lore_item_data["category"] = "OTHER_LORE"
                    lore_obj = await crud_lore_item.create_lore_item(db, LoreItemCreate(**lore_item_data), created_world_id, user_id, dummy_bg_tasks, extraction_model_config.id if extraction_model_config else None)
                    logger.info(f"JOB_ID {job_id}: Successfully created lore item '{lore_item_data.get('title')}' from document with database ID: {lore_obj.id}")
                except Exception as e: 
                    logger.error(f"JOB_ID {job_id}: Failed to create lore item '{lore_item_data.get('title')}' from document: {e}", exc_info=True)
            try:
                await db.commit()
                logger.info(f"JOB_ID {job_id}: Successfully committed World ID {created_world_id} and its extracted elements from document.")
            except Exception as commit_error:
                logger.error(f"JOB_ID {job_id}: Failed to commit database transaction for document extraction: {commit_error}", exc_info=True)
                await db.rollback()
                raise
            
            # Generate world description using AI after elements are created
            try:
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Generating world description...")
                
                # Create a summary of the world based on extracted elements
                world_summary = f"World created from document '{original_filename}' containing:\n"
                world_summary += f"- {len(characters_data)} characters\n"
                world_summary += f"- {len(locations_data)} locations\n" 
                world_summary += f"- {len(lore_data)} lore items\n\n"
                
                # Add sample content from the document for context (first 2000 chars)
                sample_content = full_text[:2000] + ("..." if len(full_text) > 2000 else "")
                world_summary += f"Sample content:\n{sample_content}"
                
                # Use the same model to generate a world description
                world_desc_prompt = """You are a world-building expert. Based on the provided document summary and extracted elements, create a compelling 2-3 paragraph description of this fictional world that captures its essence, tone, and key themes.

The description should:
- Capture the overall atmosphere and setting
- Mention key themes or concepts
- Be engaging and immersive
- Avoid listing individual characters or locations (focus on the world as a whole)

Respond with ONLY the world description text, no JSON or formatting."""

                try:
                    world_desc_response, _, _ = await _call_ai_for_text_generation(
                        extraction_model_config, world_desc_prompt, world_summary, job_id
                    )
                    
                    # Update the world with the generated description
                    world_to_update = await db.get(World, created_world_id)
                    if world_to_update and world_desc_response.strip():
                        world_to_update.description = world_desc_response.strip()
                        db.add(world_to_update)
                        await db.commit()
                        logger.info(f"JOB_ID {job_id}: Successfully updated world description for World ID {created_world_id}")
                    
                except Exception as desc_error:
                    logger.warning(f"JOB_ID {job_id}: Failed to generate world description: {desc_error}")
                    # Don't fail the entire job if world description generation fails
                    
            except Exception as world_desc_error:
                logger.warning(f"JOB_ID {job_id}: World description generation failed: {world_desc_error}")
                # Don't fail the entire job if world description generation fails
            
        # Phase 2: Run RAG indexing
        if created_world_id:
            async with async_session_local() as db:
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Loading world elements for indexing...")
                all_elements_db = await asyncio.gather(crud_character.get_characters_by_world(db, created_world_id, limit=500), crud_location.get_locations_by_world(db, created_world_id, limit=500), crud_lore_item.get_lore_items_by_world(db, created_world_id, limit=500))

            rag_tasks = []
            dummy_bg_tasks_for_rag = BackgroundTasks()
            # Pass the same model configuration used for element extraction to RAG tasks
            selected_model_id = extraction_model_config.id if extraction_model_config else None
            logger.info(f"JOB_ID {job_id}: Using model ID {selected_model_id} for RAG text generation from document (same as extraction)")
            for char in all_elements_db[0]: rag_tasks.append(generate_and_index_world_element_rag_text_task("character", char.id, user_id, created_world_id, dummy_bg_tasks_for_rag, selected_model_id))
            for loc in all_elements_db[1]: rag_tasks.append(generate_and_index_world_element_rag_text_task("location", loc.id, user_id, created_world_id, dummy_bg_tasks_for_rag, selected_model_id))
            for lore in all_elements_db[2]: rag_tasks.append(generate_and_index_world_element_rag_text_task("lore_item", lore.id, user_id, created_world_id, dummy_bg_tasks_for_rag, selected_model_id))
            
            if rag_tasks:
                # Update status with the actual number of elements to index
                async with async_session_local() as status_db:
                    await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, f"Indexing {len(rag_tasks)} elements for search (processing sequentially to avoid rate limits)...")
                logger.info(f"JOB_ID {job_id}: Starting sequential RAG indexing for {len(rag_tasks)} elements from document to avoid rate limits.")
                successful_tasks = 0
                failed_tasks = 0
                
                # Process tasks sequentially with delay to avoid Azure rate limits
                for i, task in enumerate(rag_tasks):
                    try:
                        # Update status every 5 elements
                        if i % 5 == 0:
                            async with async_session_local() as status_db:
                                await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, f"Indexing element {i+1}/{len(rag_tasks)} for search...")
                        
                        # Add timeout to prevent hanging
                        await asyncio.wait_for(task, timeout=120.0)  # 2 minute timeout per task
                        successful_tasks += 1
                        logger.info(f"JOB_ID {job_id}: Completed RAG task {i+1}/{len(rag_tasks)}")
                        
                        # Add delay between AI calls to respect rate limits
                        if i < len(rag_tasks) - 1:  # Don't delay after the last task
                            await asyncio.sleep(5)  # 5 second delay between calls to be more conservative
                    except asyncio.TimeoutError:
                        failed_tasks += 1
                        logger.error(f"JOB_ID {job_id}: RAG task {i+1} timed out after 2 minutes")
                        # Continue with next task
                    except Exception as task_error:
                        failed_tasks += 1
                        logger.error(f"JOB_ID {job_id}: RAG task {i+1} failed: {task_error}", exc_info=True)
                        # Continue with next task even if one fails
                
                logger.info(f"JOB_ID {job_id}: Finished sequential RAG indexing from document. Success: {successful_tasks}, Failed: {failed_tasks}")
                
                # Update final status with results
                if failed_tasks > 0:
                    async with async_session_local() as status_db:
                        await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, f"RAG indexing completed with some failures: {successful_tasks} successful, {failed_tasks} failed")

            # Process the uploaded document for RAG indexing
            if document_record:
                try:
                    async with async_session_local() as status_db:
                        await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, "Processing document for search indexing...")
                    
                    # Create a new job ID for document RAG processing
                    doc_job_id = str(uuid.uuid4())
                    
                    logger.info(f"JOB_ID {job_id}: Starting document RAG processing with job ID: {doc_job_id}")
                    
                    # Process document for RAG (this handles chunking, embedding, and indexing)
                    await process_uploaded_document_task(
                        job_id=doc_job_id,
                        db_document_id=document_record.id,
                        file_path_on_disk=temp_file_path
                    )
                    
                    logger.info(f"JOB_ID {job_id}: Document RAG processing completed successfully")
                    
                except Exception as doc_rag_error:
                    logger.error(f"JOB_ID {job_id}: Failed to process document for RAG indexing: {doc_rag_error}", exc_info=True)
                    # Don't fail the entire job if document RAG processing fails
                    async with async_session_local() as status_db:
                        await crud_job_status.update_job_status(status_db, job_id, JobStateEnum.RUNNING, "Document RAG processing failed, but world creation was successful")
            else:
                logger.warning(f"JOB_ID {job_id}: No document record created, skipping document RAG processing")

            # Complete the job successfully
            async with async_session_local() as db:
                if document_record:
                    result_msg = f"Successfully created world '{world_name}' (ID: {created_world_id}) with AI-generated description and imported elements from document '{original_filename}'. Document added to library and indexed for search."
                else:
                    result_msg = f"Successfully created world '{world_name}' (ID: {created_world_id}) with AI-generated description and imported elements from document '{original_filename}'."
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.COMPLETED, "Processing complete!", result_message=result_msg, world_id=created_world_id)
        else:
            raise ValueError("World was not created, cannot proceed to RAG indexing.")

    except Exception as e:
        error_message = f"Failed to create world from document '{original_filename}': {str(e)[:400]}"
        logger.error(error_message, exc_info=True)
        if created_world_id:
            async with async_session_local() as cleanup_db:
                world_to_delete = await cleanup_db.get(World, created_world_id)
                if world_to_delete: await cleanup_db.delete(world_to_delete); await cleanup_db.commit()
        async with async_session_local() as error_db:
            await crud_job_status.update_job_status(error_db, job_id, JobStateEnum.FAILED, "An error occurred.", result_message=error_message)
    finally:
        if os.path.exists(temp_file_path):
            shutil.rmtree(os.path.dirname(temp_file_path), ignore_errors=True)