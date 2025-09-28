# app/services/sk_plugins/storytelling_plugin_setup.py
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
import logging

from app.core.config import settings
from app.services.sk_constants import STORYTELLING_PLUGIN_NAME # Import the constant

logger = logging.getLogger(__name__)

# Plugin Name Constant is now imported.

def register_storytelling_functions(kernel_instance: sk.Kernel, chat_service_id: str, prompt_loader: callable):
    logger.info(f"SK_PLUGIN_SETUP ({STORYTELLING_PLUGIN_NAME}): Registering functions...")

    # Function: GenerateActNarrativeOnly
    try:
        act_narrative_only_prompt_text = prompt_loader("generate_act_narrative_only.txt")
        act_narrative_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_narrative"],
            temperature=settings.AI_TEMPERATURE_SETTINGS["act_narrative"], 
            top_p=settings.AI_TOP_P_SETTINGS["act_narrative"]
        )
        act_narrative_prompt_config = PromptTemplateConfig(
            template=act_narrative_only_prompt_text, 
            name="GenerateActNarrativeOnly", 
            template_format="semantic-kernel", 
            description="Generates or modifies narrative content for an Act based on user instruction and context.", 
            input_variables=[],
            execution_settings={chat_service_id: act_narrative_exec_settings}
        )
        kernel_instance.add_function(
            function_name="GenerateActNarrativeOnly", 
            plugin_name=STORYTELLING_PLUGIN_NAME, 
            prompt_template_config=act_narrative_prompt_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORYTELLING_PLUGIN_NAME}): Registered GenerateActNarrativeOnly.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORYTELLING_PLUGIN_NAME}): ERROR registering GenerateActNarrativeOnly: {e}", exc_info=True)

    # Function: GenerateSceneNarrativeOnly
    try:
        scene_narrative_only_prompt_text = prompt_loader("generate_scene_narrative_only.txt")
        scene_narrative_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["scene_narrative"],
            temperature=settings.AI_TEMPERATURE_SETTINGS["scene_narrative"], 
            top_p=settings.AI_TOP_P_SETTINGS["scene_narrative"]
        )
        scene_narrative_prompt_config = PromptTemplateConfig(
            template=scene_narrative_only_prompt_text, 
            name="GenerateSceneNarrativeOnly", 
            template_format="semantic-kernel", 
            description="Generates or modifies narrative content for a Scene based on user instruction and context.", 
            input_variables=[],
            execution_settings={chat_service_id: scene_narrative_exec_settings}
        )
        kernel_instance.add_function(
            function_name="GenerateSceneNarrativeOnly", 
            plugin_name=STORYTELLING_PLUGIN_NAME, 
            prompt_template_config=scene_narrative_prompt_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORYTELLING_PLUGIN_NAME}): Registered GenerateSceneNarrativeOnly.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORYTELLING_PLUGIN_NAME}): ERROR registering GenerateSceneNarrativeOnly: {e}", exc_info=True)

    logger.info(f"SK_PLUGIN_SETUP ({STORYTELLING_PLUGIN_NAME}): Function registration attempts complete.")