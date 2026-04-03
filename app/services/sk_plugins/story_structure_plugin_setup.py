"""Service helpers for story structure plugin setup."""

# app/services/sk_plugins/story_structure_plugin_setup.py
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
from semantic_kernel.prompt_template.input_variable import InputVariable
import logging

from app.core.config import settings # For SCENE_EXTRACTION_MAX_TOKENS and TEMPERATURE
from app.services.sk_constants import STORY_STRUCTURE_PLUGIN_NAME # Import the constant

logger = logging.getLogger(__name__)

# Plugin Name Constant is now imported.

def register_story_structure_functions(kernel_instance: sk.Kernel, chat_service_id: str, prompt_loader: callable):
    """Provide service support for register story structure functions."""
    logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Registering functions...")

    # Function: ExtractScenesFromAct
    try:
        scene_extraction_prompt_text = prompt_loader("scene_extraction.txt")
        
        scene_extraction_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.SCENE_EXTRACTION_MAX_TOKENS, 
            temperature=settings.SCENE_EXTRACTION_TEMPERATURE, 
            top_p=settings.AI_TOP_P_SETTINGS["scene_extraction"],
            response_format={"type": "json_object"}
        )
        
        scene_extraction_prompt_config = PromptTemplateConfig(
            template=scene_extraction_prompt_text, 
            name="ExtractScenesFromAct", 
            template_format="semantic-kernel", 
            description="Analyzes Act content (Markdown) and extracts distinct scenes as structured JSON.", 
            input_variables=[],
            execution_settings={chat_service_id: scene_extraction_exec_settings}
        )
        
        kernel_instance.add_function(
            function_name="ExtractScenesFromAct", 
            plugin_name=STORY_STRUCTURE_PLUGIN_NAME, 
            prompt_template_config=scene_extraction_prompt_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Registered ExtractScenesFromAct.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): ERROR registering ExtractScenesFromAct: {e}", exc_info=True)

    # Function: GenerateStoryStructure
    try:
        logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Starting GenerateStoryStructure registration...")
        
        story_generation_prompt_text = prompt_loader("story_generation.txt")
        logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Loaded prompt text (length: {len(story_generation_prompt_text)})")
        
        story_generation_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.STORY_GENERATION_MAX_TOKENS, 
            temperature=settings.STORY_GENERATION_TEMPERATURE, 
            top_p=settings.AI_TOP_P_SETTINGS["story_generation"],
            response_format={"type": "json_object"}
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Created execution settings")
        
        story_generation_prompt_config = PromptTemplateConfig(
            template=story_generation_prompt_text, 
            name="GenerateStoryStructure", 
            template_format="semantic-kernel", 
            description="Generates a complete three-act story structure in JSON format using provided world elements.", 
            input_variables=[
                InputVariable(name="characters", description="Formatted list of characters", is_required=True),
                InputVariable(name="locations", description="Formatted list of locations", is_required=True),
                InputVariable(name="lore_items", description="Formatted list of lore items", is_required=True),
                InputVariable(name="author_concept", description="Author's concept or story idea", is_required=False),
                InputVariable(name="story_genre", description="Selected story genre", is_required=True),
                InputVariable(name="story_tone", description="Selected story tone", is_required=True),
                InputVariable(name="primary_conflict_type", description="Selected primary conflict type", is_required=True)
            ],
            execution_settings={chat_service_id: story_generation_exec_settings}
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Created prompt config")
        
        kernel_instance.add_function(
            function_name="GenerateStoryStructure", 
            plugin_name=STORY_STRUCTURE_PLUGIN_NAME, 
            prompt_template_config=story_generation_prompt_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): add_function call completed")
        
        # Verify the function was actually added
        if STORY_STRUCTURE_PLUGIN_NAME in kernel_instance.plugins:
            plugin = kernel_instance.plugins[STORY_STRUCTURE_PLUGIN_NAME]
            functions_metadata = plugin.get_functions_metadata()
            function_names = [func.name for func in functions_metadata]
            logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Functions after add: {function_names}")
        
        logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Registered GenerateStoryStructure.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): ERROR registering GenerateStoryStructure: {e}", exc_info=True)

    logger.info(f"SK_PLUGIN_SETUP ({STORY_STRUCTURE_PLUGIN_NAME}): Function registration attempts complete.")
