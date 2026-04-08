"""Service helpers for world generation plugin setup."""

# app/services/sk_plugins/world_generation_plugin_setup.py
from app.services.langgraph_kernel import OpenAIChatPromptExecutionSettings, PromptTemplateConfig
import logging

from app.core.config import settings
from app.services.sk_constants import WORLD_GENERATION_PLUGIN_NAME

logger = logging.getLogger(__name__)

def register_world_generation_functions(kernel_instance, chat_service_id: str, prompt_loader: callable):
    """Provide service support for register world generation functions."""
    logger.info(f"SK_PLUGIN_SETUP ({WORLD_GENERATION_PLUGIN_NAME}): Registering functions...")

    # Function: GenerateWorldFromBookTitle (Existing)
    try:
        generate_world_from_book_prompt_text = prompt_loader("generate_world_from_book.txt")
        world_gen_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["world_generation"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["world_generation"],
            top_p=settings.AI_TOP_P_SETTINGS["world_generation"], 
            response_format={"type": "json_object"}
        )
        world_gen_config = PromptTemplateConfig(
            template=generate_world_from_book_prompt_text, name="GenerateWorldFromBookTitle",
            template_format="semantic-kernel", description="Generates a structured JSON world definition based on a book title.",
            input_variables=[], execution_settings={chat_service_id: world_gen_exec_settings}
        )
        kernel_instance.add_function(
            function_name="GenerateWorldFromBookTitle", plugin_name=WORLD_GENERATION_PLUGIN_NAME,
            prompt_template_config=world_gen_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({WORLD_GENERATION_PLUGIN_NAME}): Registered GenerateWorldFromBookTitle.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({WORLD_GENERATION_PLUGIN_NAME}): ERROR registering GenerateWorldFromBookTitle: {e}", exc_info=True)

    # --- NEW FUNCTION: ExtractWorldElementsFromText ---
    try:
        extract_elements_prompt_text = prompt_loader("extract_world_elements_from_text.txt")
        extract_elements_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["world_elements_extraction"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["world_elements_extraction"],
            top_p=settings.AI_TOP_P_SETTINGS["world_elements_extraction"], 
            response_format={"type": "json_object"}
        )
        extract_elements_config = PromptTemplateConfig(
            template=extract_elements_prompt_text, name="ExtractWorldElementsFromText",
            template_format="semantic-kernel", description="Extracts characters, locations, and lore from a block of text.",
            input_variables=[], execution_settings={chat_service_id: extract_elements_exec_settings}
        )
        kernel_instance.add_function(
            function_name="ExtractWorldElementsFromText", plugin_name=WORLD_GENERATION_PLUGIN_NAME,
            prompt_template_config=extract_elements_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({WORLD_GENERATION_PLUGIN_NAME}): Registered ExtractWorldElementsFromText.")
    except Exception as e:
        logger.error(f"SK_PLUGIN_SETUP ({WORLD_GENERATION_PLUGIN_NAME}): ERROR registering ExtractWorldElementsFromText: {e}", exc_info=True)
    # --- END NEW FUNCTION ---

    logger.info(f"SK_PLUGIN_SETUP ({WORLD_GENERATION_PLUGIN_NAME}): Function registration attempts complete.")
