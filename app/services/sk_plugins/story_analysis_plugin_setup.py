"""Service helpers for story analysis plugin setup."""

# app/services/sk_plugins/story_analysis_plugin_setup.py
from app.services.langgraph_kernel import OpenAIChatPromptExecutionSettings, PromptTemplateConfig
import logging

from app.core.config import settings
from app.services.sk_constants import STORY_ANALYSIS_PLUGIN_NAME # Import the constant

logger = logging.getLogger(__name__)

# Plugin Name Constant is now imported, no local definition needed.

def register_story_analysis_functions(kernel_instance, chat_service_id: str, prompt_loader: callable):
    """Provide service support for register story analysis functions."""
    logger.info(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): Registering functions...")

    # Function: ReviewActContentEnhanced
    try:
        enhanced_act_review_prompt_text = prompt_loader("enhanced_act_review_prompt.txt")
        act_review_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_review"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["act_review"], 
            top_p=settings.AI_TOP_P_SETTINGS["act_review"],
            response_format={"type": "json_object"}) 
        act_review_prompt_config = PromptTemplateConfig(
            template=enhanced_act_review_prompt_text, name="ReviewActContentEnhanced",
            template_format="semantic-kernel", description="Analyzes Act content for feedback with metrics.",
            input_variables=[], 
            execution_settings={chat_service_id: act_review_exec_settings})
        kernel_instance.add_function(function_name="ReviewActContentEnhanced", plugin_name=STORY_ANALYSIS_PLUGIN_NAME, prompt_template_config=act_review_prompt_config)
        logger.info(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): Registered ReviewActContentEnhanced.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): ERROR registering ReviewActContentEnhanced: {e}", exc_info=True)

    # Function: GenerateActMetadata
    try:
        act_metadata_generation_prompt_text = prompt_loader("generate_act_metadata.txt")
        act_metadata_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_metadata"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["act_metadata"], 
            top_p=settings.AI_TOP_P_SETTINGS["act_metadata"], 
            response_format={"type": "json_object"})
        act_metadata_prompt_config = PromptTemplateConfig(
            template=act_metadata_generation_prompt_text, name="GenerateActMetadata", 
            template_format="semantic-kernel", description="Generates Act metadata like summary points and character developments.", 
            input_variables=[], 
            execution_settings={chat_service_id: act_metadata_exec_settings})
        kernel_instance.add_function(function_name="GenerateActMetadata", plugin_name=STORY_ANALYSIS_PLUGIN_NAME, prompt_template_config=act_metadata_prompt_config)
        logger.info(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): Registered GenerateActMetadata.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): ERROR registering GenerateActMetadata: {e}", exc_info=True)

    # Function: GenerateSceneMetadata
    try:
        scene_metadata_generation_prompt_text = prompt_loader("generate_scene_metadata.txt")
        scene_metadata_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["scene_metadata"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["scene_metadata"], 
            top_p=settings.AI_TOP_P_SETTINGS["scene_metadata"], 
            response_format={"type": "json_object"})
        scene_metadata_prompt_config = PromptTemplateConfig(
            template=scene_metadata_generation_prompt_text, name="GenerateSceneMetadata", 
            template_format="semantic-kernel", description="Generates scene metadata like mood, characters, and plot points.", 
            input_variables=[], 
            execution_settings={chat_service_id: scene_metadata_exec_settings})
        kernel_instance.add_function(function_name="GenerateSceneMetadata", plugin_name=STORY_ANALYSIS_PLUGIN_NAME, prompt_template_config=scene_metadata_prompt_config)
        logger.info(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): Registered GenerateSceneMetadata.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): ERROR registering GenerateSceneMetadata: {e}", exc_info=True)

    # Function: GenerateTextSummary
    try:
        text_summary_prompt_text = prompt_loader("generate_text_summary.txt")
        text_summary_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS.get("text_summary", 300), 
            temperature=settings.AI_TEMPERATURE_SETTINGS.get("text_summary", 0.3), 
            top_p=settings.AI_TOP_P_SETTINGS.get("text_summary", 0.95))
        text_summary_prompt_config = PromptTemplateConfig(
            template=text_summary_prompt_text, name="GenerateTextSummary", 
            template_format="semantic-kernel", description="Generates a concise summary of provided text.", 
            input_variables=[], 
            execution_settings={chat_service_id: text_summary_exec_settings})
        kernel_instance.add_function(function_name="GenerateTextSummary", plugin_name=STORY_ANALYSIS_PLUGIN_NAME, prompt_template_config=text_summary_prompt_config)
        logger.info(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): Registered GenerateTextSummary.")
    except Exception as e: 
        logger.error(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): ERROR registering GenerateTextSummary: {e}", exc_info=True)

    logger.info(f"SK_PLUGIN_SETUP ({STORY_ANALYSIS_PLUGIN_NAME}): Function registration attempts complete.")
