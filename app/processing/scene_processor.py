# /ai_rag_story_app/app/processing/scene_processor.py

import asyncio # Not strictly used in this version but often useful in processing tasks
import json
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from markdownify import markdownify as md 

# --- Core Application Imports ---
from app.db.database import async_session_local 
from app.models.act import Act # For type hinting if needed
from app.crud import scene as crud_scene
# from app.crud import act as crud_act # Not directly used in this task after act_id is passed
from app.schemas.scene import SceneCreate # For validation if desired, though not strictly used for direct creation here

# --- Semantic Kernel Imports ---
from app.services.semantic_kernel_setup import (
    kernel,
    extract_scenes_from_act_function, 
    SCENE_EXTRACTION_SYSTEM_PROMPT # This is the system prompt string for the SK function
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.contents.chat_message_content import ChatMessageContent 
from semantic_kernel.functions.function_result import FunctionResult
from openai import APIError 

logger = logging.getLogger(__name__)

async def generate_and_save_scenes_for_act_task(
    db_act_id: int,
    act_content_html: str, 
    story_id: int, # For logging/context, not directly used in scene creation itself here
    user_id: int   # For logging/context
):
    """
    Background task to generate scenes from an Act's content using an LLM,
    then delete old scenes and save the new ones.
    """
    logger.info(f"Starting scene generation task for Act ID: {db_act_id}, User ID: {user_id}, Story ID: {story_id}")

    async with async_session_local() as db: # type: AsyncSession
        try:
            act_content_markdown = "No content provided or content was only whitespace."
            if act_content_html and act_content_html.strip():
                try:
                    # Convert HTML from Quill to Markdown for the LLM
                    act_content_markdown = md(act_content_html, heading_style="ATX", bullets="*")
                    logger.info(f"Successfully converted Act ID {db_act_id} content to Markdown. Length: {len(act_content_markdown)}")
                except Exception as e_md:
                    logger.error(f"Error converting Act ID {db_act_id} content to Markdown: {e_md}. Using raw HTML as fallback.", exc_info=True)
                    act_content_markdown = act_content_html # Fallback to HTML if conversion fails
            else:
                logger.warning(f"Act ID {db_act_id} has no HTML content to process for scene extraction. Aborting task.")
                # Optionally, delete existing scenes if no content means no scenes should exist
                await crud_scene.delete_scenes_for_act(db, act_id=db_act_id)
                await db.commit()  # Commit the deletion
                logger.info(f"Cleared any existing scenes for Act ID {db_act_id} due to no source content.")
                return 

            if not extract_scenes_from_act_function:
                logger.error(f"Scene extraction SK function (ExtractScenesFromAct) not available. Cannot process Act ID: {db_act_id}.")
                return

            # The SCENE_EXTRACTION_SYSTEM_PROMPT is now loaded from file in semantic_kernel_setup.py
            # and is part of the extract_scenes_from_act_function's definition.
            # We only need to pass the act_content_to_analyze.
            kernel_args = KernelArguments(
                # scene_extraction_system_prompt is part of the function's definition
                act_content_to_analyze=act_content_markdown
            )
            logger.info(f"Invoking Semantic Kernel function 'ExtractScenesFromAct' for Act ID: {db_act_id}.")
            
            llm_json_string: Optional[str] = None
            try:
                sk_result: FunctionResult = await kernel.invoke(extract_scenes_from_act_function, arguments=kernel_args)
                
                if sk_result and sk_result.value:
                    actual_content_object = sk_result.value
                    if isinstance(actual_content_object, list) and actual_content_object:
                        if isinstance(actual_content_object[0], ChatMessageContent):
                            llm_json_string = actual_content_object[0].content
                        else: 
                            llm_json_string = str(actual_content_object[0])
                    elif isinstance(actual_content_object, ChatMessageContent):
                        llm_json_string = actual_content_object.content
                    else: 
                        llm_json_string = str(actual_content_object)
                
                logger.info(f"LLM response string received for scene extraction (Act ID {db_act_id}). Length: {len(llm_json_string) if llm_json_string else 0}")
                logger.debug(f"Raw LLM JSON string for scene extraction (Act ID {db_act_id}): {llm_json_string}")

            except APIError as e_api:
                logger.error(f"OpenAI APIError during scene extraction for Act ID {db_act_id}: {e_api.message}", exc_info=True)
                # Potentially update act status to error here if you had such a field for acts
                return
            except Exception as e_sk:
                logger.error(f"Error invoking Semantic Kernel for scene extraction (Act ID {db_act_id}): {e_sk}", exc_info=True)
                return

            if not llm_json_string or not llm_json_string.strip():
                logger.warning(f"LLM did not return content for scene extraction (Act ID {db_act_id}). Response string was empty or None.")
                await crud_scene.delete_scenes_for_act(db, act_id=db_act_id) # Clear existing scenes if AI returns nothing
                return
            
            # Attempt to strip potential markdown code block fences if present
            temp_json_string = llm_json_string.strip()
            if temp_json_string.startswith("```json") and temp_json_string.endswith("```"):
                llm_json_string = temp_json_string[7:-3].strip()
            elif temp_json_string.startswith("```") and temp_json_string.endswith("```"):
                 llm_json_string = temp_json_string[3:-3].strip()

            extracted_scenes_data: List[Dict[str, Any]] = []
            try:
                parsed_data = json.loads(llm_json_string)
                if isinstance(parsed_data, dict) and "scenes" in parsed_data and isinstance(parsed_data["scenes"], list):
                    extracted_scenes_data = parsed_data["scenes"]
                    logger.info(f"Successfully parsed scenes from root object {{'scenes': [...]}} for Act ID {db_act_id}.")
                elif isinstance(parsed_data, list):
                    extracted_scenes_data = parsed_data
                    logger.info(f"Successfully parsed scenes from direct list [...] for Act ID {db_act_id}.")
                # --- MODIFIED: Handle case where LLM returns a single scene object instead of an array ---
                elif isinstance(parsed_data, dict) and all(k in parsed_data for k in ["title", "summary", "content"]): 
                    logger.warning(f"LLM returned a single scene object instead of an array for Act ID {db_act_id}. Wrapping it in a list.")
                    extracted_scenes_data = [parsed_data] 
                # --- END MODIFICATION ---
                else:
                    logger.warning(f"LLM response for scenes was not a list, a dict with a 'scenes' key, or a single scene-like object for Act ID {db_act_id}. Found type: {type(parsed_data)}. Content preview: {str(parsed_data)[:200]}")
                    extracted_scenes_data = [] 
            except json.JSONDecodeError as e_json:
                logger.error(f"Failed to parse JSON response from LLM for scene extraction (Act ID {db_act_id}): {e_json}", exc_info=True)
                logger.error(f"Problematic JSON string for Act ID {db_act_id} (after attempting to strip fences): {llm_json_string}")
                # Don't delete existing scenes if we just failed to parse new ones, unless intended
                return

            logger.info(f"Deleting existing scenes for Act ID: {db_act_id} before adding new ones.")
            num_deleted = await crud_scene.delete_scenes_for_act(db, act_id=db_act_id)
            await db.commit()  # Commit the deletion before creating new scenes
            logger.info(f"Deleted {num_deleted} old scenes for Act ID: {db_act_id}.")

            if not extracted_scenes_data: # Check after parsing and potential single-item wrapping
                logger.info(f"No valid scenes were extracted or formatted by the AI for Act ID: {db_act_id}. No new scenes will be created.")
                return # No new scenes to create

            scenes_to_create_validated: List[Dict[str, Any]] = []
            for i, scene_data_from_ai in enumerate(extracted_scenes_data):
                if not isinstance(scene_data_from_ai, dict):
                    logger.warning(f"AI-generated scene data at index {i} is not a dictionary for Act ID {db_act_id}. Skipping. Data: {scene_data_from_ai}")
                    continue
                try:
                    # Map AI output keys to Scene model fields
                    # create_multiple_scenes will assign scene_number incrementally.
                    plot_points_value = scene_data_from_ai.get("plot_points")
                    if isinstance(plot_points_value, list):
                        plot_points_str = "\n".join(filter(None, [str(p).strip() for p in plot_points_value]))
                    elif isinstance(plot_points_value, str):
                        plot_points_str = plot_points_value.strip()
                    else:
                        plot_points_str = None

                    scene_to_add = {
                        "title": scene_data_from_ai.get("title"),
                        "summary": scene_data_from_ai.get("summary"),
                        "content": scene_data_from_ai.get("content"), # This might be Markdown or plain text from LLM
                        "characters_present": scene_data_from_ai.get("characters_present"),
                        "plot_points": plot_points_str,
                        "mood": scene_data_from_ai.get("mood")
                    }
                    # Optional: Validate with SceneCreate schema (excluding scene_number)
                    # SceneCreate(**{k:v for k,v in scene_to_add.items() if k != 'scene_number'}) 
                    scenes_to_create_validated.append(scene_to_add) 
                except Exception as e_val: 
                    logger.warning(f"Validation or processing error for AI-generated scene data for Act ID {db_act_id}, scene index {i}: {e_val}. Skipping this scene. Data: {scene_data_from_ai}")
                    continue 

            if not scenes_to_create_validated:
                logger.warning(f"No valid scenes to create for Act ID {db_act_id} after AI processing and validation.")
                return

            logger.info(f"Creating {len(scenes_to_create_validated)} new scenes for Act ID: {db_act_id}.")
            await crud_scene.create_multiple_scenes(
                db=db,
                scenes_data=scenes_to_create_validated, # This is List[Dict], not List[SceneCreate]
                act_id=db_act_id
            )
            
            # Commit the transaction to ensure scenes are saved to database
            await db.commit()
            logger.info(f"Successfully created, saved, and committed new scenes for Act ID: {db_act_id}.")

        except Exception as e:
            logger.error(f"Unhandled error during scene generation task for Act ID {db_act_id}: {e}", exc_info=True)
            # Rollback transaction on error
            await db.rollback()
        finally:
            logger.info(f"Scene generation task finished for Act ID: {db_act_id}")