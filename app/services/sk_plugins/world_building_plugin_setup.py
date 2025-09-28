# app/services/sk_plugins/world_building_plugin_setup.py
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
import logging

from app.core.config import settings 
from app.services.sk_constants import WORLD_BUILDING_PLUGIN_NAME # Import the constant

logger = logging.getLogger(__name__)

# Plugin Name Constant is now imported.

def register_world_building_functions(kernel_instance: sk.Kernel, chat_service_id: str, prompt_loader: callable):
    logger.info(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): Registering functions...")

    rag_doc_exec_settings = AzureChatPromptExecutionSettings(
        service_id=chat_service_id, 
        max_tokens=settings.AI_MAX_TOKEN_SETTINGS["rag_conversion"],
        temperature=settings.AI_TEMPERATURE_SETTINGS["rag_conversion"],
        top_p=settings.AI_TOP_P_SETTINGS["rag_conversion"]
    )

    # Function: ConvertCharacterToRAGText
    try:
        character_to_rag_text_prompt = prompt_loader("character_to_rag_text.txt")
        char_to_rag_config = PromptTemplateConfig(
            template=character_to_rag_text_prompt, 
            name="ConvertCharacterToRAGText", 
            template_format="semantic-kernel", 
            description="Converts structured character data into a concise descriptive paragraph for RAG.", 
            input_variables=[],
            execution_settings={chat_service_id: rag_doc_exec_settings}
        )
        kernel_instance.add_function(
            function_name="ConvertCharacterToRAGText", 
            plugin_name=WORLD_BUILDING_PLUGIN_NAME, 
            prompt_template_config=char_to_rag_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): Registered ConvertCharacterToRAGText.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): ERROR registering ConvertCharacterToRAGText: {e}", exc_info=True)

    # Function: ConvertLocationToRAGText
    try:
        location_to_rag_text_prompt = prompt_loader("location_to_rag_text.txt")
        loc_to_rag_config = PromptTemplateConfig(
            template=location_to_rag_text_prompt, 
            name="ConvertLocationToRAGText", 
            template_format="semantic-kernel", 
            description="Converts structured location data into a concise descriptive paragraph for RAG.", 
            input_variables=[], 
            execution_settings={chat_service_id: rag_doc_exec_settings}
        )
        kernel_instance.add_function(
            function_name="ConvertLocationToRAGText", 
            plugin_name=WORLD_BUILDING_PLUGIN_NAME, 
            prompt_template_config=loc_to_rag_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): Registered ConvertLocationToRAGText.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): ERROR registering ConvertLocationToRAGText: {e}", exc_info=True)

    # Function: ConvertLoreItemToRAGText
    try:
        lore_item_to_rag_text_prompt = prompt_loader("lore_item_to_rag_text.txt")
        lore_to_rag_config = PromptTemplateConfig(
            template=lore_item_to_rag_text_prompt, 
            name="ConvertLoreItemToRAGText", 
            template_format="semantic-kernel", 
            description="Converts structured lore item data into a concise descriptive paragraph for RAG.", 
            input_variables=[], 
            execution_settings={chat_service_id: rag_doc_exec_settings}
        )
        kernel_instance.add_function(
            function_name="ConvertLoreItemToRAGText", 
            plugin_name=WORLD_BUILDING_PLUGIN_NAME, 
            prompt_template_config=lore_to_rag_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): Registered ConvertLoreItemToRAGText.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): ERROR registering ConvertLoreItemToRAGText: {e}", exc_info=True)

    # Function: GenerateCharacterBackstory
    try:
        character_backstory_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS.get("character_generation", 1000),
            temperature=settings.AI_TEMPERATURE_SETTINGS.get("character_generation", 0.7),
            top_p=settings.AI_TOP_P_SETTINGS.get("character_generation", 1.0)
        )
        
        character_backstory_prompt = prompt_loader("character_backstory_generation.txt")
        char_backstory_config = PromptTemplateConfig(
            template=character_backstory_prompt, 
            name="GenerateCharacterBackstory", 
            template_format="semantic-kernel", 
            description="Generates compelling character backstory based on character details.", 
            input_variables=[], 
            execution_settings={chat_service_id: character_backstory_exec_settings}
        )
        kernel_instance.add_function(
            function_name="GenerateCharacterBackstory", 
            plugin_name=WORLD_BUILDING_PLUGIN_NAME, 
            prompt_template_config=char_backstory_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): Registered GenerateCharacterBackstory.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): ERROR registering GenerateCharacterBackstory: {e}", exc_info=True)

    logger.info(f"SK_PLUGIN_SETUP ({WORLD_BUILDING_PLUGIN_NAME}): Function registration attempts complete.")