# /ai_rag_story_app/app/services/semantic_kernel_setup.py

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
    AzureChatPromptExecutionSettings
)
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
import os
from typing import Optional
import logging
from app.core.config import settings
from .rag_retrieval import RetrievalPlugin
from .sk_plugins.story_brainstorm_plugin_setup import setup_story_brainstorm_plugin

logger = logging.getLogger(__name__)

_CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(_CURRENT_FILE_DIR, '..', 'prompts', 'system')
BASIC_STORY_PROMPTS_DIR = os.path.join(_CURRENT_FILE_DIR, '..', 'prompts', 'basic_story')

STORYTELLING_PLUGIN_NAME = "StorytellingPlugin"
STORY_ANALYSIS_PLUGIN_NAME = "StoryAnalysisPlugin"
STORY_STRUCTURE_PLUGIN_NAME = "StoryStructurePlugin"
WORLD_BUILDING_PLUGIN_NAME = "WorldBuildingPlugin"
WORLD_GENERATION_PLUGIN_NAME = "WorldGenerationPlugin"
RETRIEVAL_PLUGIN_NAME = "Retrieval"
BASIC_STORY_PLUGIN_NAME = "basic_story"
STORY_BRAINSTORM_PLUGIN_NAME = "StoryBrainstormPlugin"

def load_prompt_from_file(filename: str) -> str:
    filepath = os.path.join(PROMPTS_DIR, filename)
    logger.debug(f"SK_SETUP: Attempting to load prompt file: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"SK_SETUP: Successfully loaded prompt from: {filepath}")
        return content
    except FileNotFoundError:
        logger.error(f"SK_SETUP: CRITICAL - Prompt file {filepath} not found.")
        raise RuntimeError(f"Essential prompt file missing: {filepath}")
    except Exception as e:
        logger.error(f"SK_SETUP: Error loading prompt file {filepath}: {e}", exc_info=True)
        raise RuntimeError(f"Error loading prompt file {filepath}: {e}")

def load_basic_story_prompt_from_file(filename: str) -> str:
    filepath = os.path.join(BASIC_STORY_PROMPTS_DIR, filename)
    logger.debug(f"SK_SETUP: Attempting to load basic story prompt file: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"SK_SETUP: Successfully loaded basic story prompt from: {filepath}")
        return content
    except FileNotFoundError:
        logger.error(f"SK_SETUP: CRITICAL - Basic story prompt file {filepath} not found.")
        raise RuntimeError(f"Essential basic story prompt file missing: {filepath}")
    except Exception as e:
        logger.error(f"SK_SETUP: Error loading basic story prompt file {filepath}: {e}", exc_info=True)
        raise RuntimeError(f"Error loading basic story prompt file {filepath}: {e}")

try:
    logger.info("SK_SETUP: Loading all system prompt files...")
    ENHANCED_ACT_REVIEW_PROMPT_TEXT = load_prompt_from_file("enhanced_act_review_prompt.txt")
    ACT_NARRATIVE_ONLY_PROMPT = load_prompt_from_file("generate_act_narrative_only.txt")
    ACT_METADATA_GENERATION_PROMPT = load_prompt_from_file("generate_act_metadata.txt")
    SCENE_NARRATIVE_ONLY_PROMPT = load_prompt_from_file("generate_scene_narrative_only.txt")
    SCENE_METADATA_GENERATION_PROMPT = load_prompt_from_file("generate_scene_metadata.txt")
    SCENE_EXTRACTION_SYSTEM_PROMPT = load_prompt_from_file("scene_extraction.txt")
    CHARACTER_TO_RAG_TEXT_PROMPT = load_prompt_from_file("character_to_rag_text.txt")
    LOCATION_TO_RAG_TEXT_PROMPT = load_prompt_from_file("location_to_rag_text.txt")
    LORE_ITEM_TO_RAG_TEXT_PROMPT = load_prompt_from_file("lore_item_to_rag_text.txt")
    GENERATE_WORLD_FROM_BOOK_PROMPT_TEXT = load_prompt_from_file("generate_world_from_book.txt")
    CHARACTER_BACKSTORY_GENERATION_PROMPT = load_prompt_from_file("character_backstory_generation.txt")
    # This was missing from the list in a previous version, ensuring it's here now.
    EXTRACT_WORLD_ELEMENTS_FROM_TEXT_PROMPT = load_prompt_from_file("extract_world_elements_from_text.txt") 
    logger.info("SK_SETUP: All system prompt files loading attempted successfully.")
    
    # Load Basic Story prompts
    logger.info("SK_SETUP: Loading Basic Story prompt files...")
    BASIC_WRITING_ASSISTANCE_PROMPT = load_basic_story_prompt_from_file("basic_writing_assistance.txt")
    CONTINUE_STORY_PROMPT = load_basic_story_prompt_from_file("continue_story.txt")
    WHAT_HAPPENS_NEXT_PROMPT = load_basic_story_prompt_from_file("what_happens_next.txt")
    IMPROVE_DIALOGUE_PROMPT = load_basic_story_prompt_from_file("improve_dialogue.txt")
    SCENE_DEVELOPMENT_PROMPT = load_basic_story_prompt_from_file("scene_development.txt")
    PLOT_BRAINSTORM_PROMPT = load_basic_story_prompt_from_file("plot_brainstorm.txt")
    WRITING_FEEDBACK_PROMPT = load_basic_story_prompt_from_file("writing_feedback.txt")
    CREATIVE_BRAINSTORM_PROMPT = load_basic_story_prompt_from_file("creative_brainstorm.txt")
    STORY_PROBLEM_SOLVER_PROMPT = load_basic_story_prompt_from_file("story_problem_solver.txt")
    CHARACTER_VOICE_DEVELOPMENT_PROMPT = load_basic_story_prompt_from_file("character_voice_development.txt")
    EMOTIONAL_DEVELOPMENT_PROMPT = load_basic_story_prompt_from_file("emotional_development.txt")
    BASIC_STORY_SUMMARY_PROMPT = load_basic_story_prompt_from_file("basic_story_summary.txt")
    BASIC_ACT_SUMMARY_PROMPT = load_basic_story_prompt_from_file("basic_act_summary.txt")
    BASIC_SCENE_SUMMARY_PROMPT = load_basic_story_prompt_from_file("basic_scene_summary.txt")
    logger.info("SK_SETUP: All Basic Story prompt files loading attempted successfully.")
except Exception as e_load_prompts:
    logger.critical(f"SK_SETUP: FAILED to load one or more essential prompt files: {e_load_prompts}", exc_info=True)
    raise RuntimeError(f"Essential prompt files for SK setup could not be loaded: {e_load_prompts}") from e_load_prompts

kernel = sk.Kernel()

def initialize_kernel(kernel_instance: sk.Kernel) -> None:
    logger.info("SK_SETUP: Initializing Semantic Kernel with Azure OpenAI services and plugins...")
    azure_openai_endpoint = str(settings.AZURE_OPENAI_ENDPOINT) if settings.AZURE_OPENAI_ENDPOINT else None
    azure_openai_api_key = settings.AZURE_OPENAI_API_KEY
    azure_openai_api_version = settings.AZURE_OPENAI_API_VERSION
    
    # --- FIX: Use the new _DEFAULT setting name ---
    chat_deployment_name = settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT
    embedding_deployment_name = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    
    chat_service_id = "azure_openai_chat_service"

    if not all([azure_openai_endpoint, azure_openai_api_key, chat_deployment_name]):
        logger.critical("SK_SETUP: Azure OpenAI CHAT configuration incomplete. SK chat features will fail.")
    else:
        try:
            kernel_instance.add_service(AzureChatCompletion(
                service_id=chat_service_id, deployment_name=chat_deployment_name, endpoint=azure_openai_endpoint,
                api_key=azure_openai_api_key, api_version=azure_openai_api_version))
            logger.info(f"SK_SETUP: Added AzureChatCompletion service (ID: {chat_service_id}, Deployment: {chat_deployment_name})")
        except Exception as e:
            logger.error(f"SK_SETUP: ERROR adding AzureChatCompletion service: {e}", exc_info=True)

    if all([azure_openai_endpoint, azure_openai_api_key, embedding_deployment_name]):
        embedding_service_id = "azure_openai_embedding_service"
        try:
            kernel_instance.add_service(AzureTextEmbedding(
                service_id=embedding_service_id, deployment_name=embedding_deployment_name, endpoint=azure_openai_endpoint,
                api_key=azure_openai_api_key, api_version=azure_openai_api_version))
            logger.info(f"SK_SETUP: Added AzureTextEmbedding service (ID: {embedding_service_id}, Deployment: {embedding_deployment_name})")
        except Exception as e:
            logger.error(f"SK_SETUP: ERROR adding AzureTextEmbedding service: {e}", exc_info=True)
    else:
        logger.warning("SK_SETUP: Azure OpenAI EMBEDDING configuration incomplete. Embedding features may fail.")

    try:
        kernel_instance.add_plugin(RetrievalPlugin(), plugin_name=RETRIEVAL_PLUGIN_NAME)
        logger.info(f"SK_SETUP: Registered RetrievalPlugin as '{RETRIEVAL_PLUGIN_NAME}'.")
    except Exception as e:
        logger.error(f"SK_SETUP: ERROR registering RetrievalPlugin: {e}", exc_info=True)

    # --- Define and Register Semantic Functions ---
    # Enhanced Act Review Function
    try:
        act_review_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_review"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["act_review"], 
            top_p=settings.AI_TOP_P_SETTINGS["act_review"],
            response_format={"type": "json_object"})
        act_review_prompt_config = PromptTemplateConfig(
            template=ENHANCED_ACT_REVIEW_PROMPT_TEXT, name="ReviewActContentEnhanced",
            template_format="semantic-kernel", description="Analyzes Act content for feedback with metrics.",
            input_variables=[], execution_settings={chat_service_id: act_review_exec_settings})
        kernel_instance.add_function(function_name="ReviewActContentEnhanced", plugin_name=STORY_ANALYSIS_PLUGIN_NAME, prompt_template_config=act_review_prompt_config)
        logger.info(f"SK_SETUP: Registered ReviewActContentEnhanced in {STORY_ANALYSIS_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering ReviewActContentEnhanced: {e}", exc_info=True)

    # Act Narrative-Only Generation
    try:
        act_narrative_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_narrative"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["act_narrative"], 
            top_p=settings.AI_TOP_P_SETTINGS["act_narrative"])
        act_narrative_prompt_config = PromptTemplateConfig(template=ACT_NARRATIVE_ONLY_PROMPT, name="GenerateActNarrativeOnly", template_format="semantic-kernel", description="Generates Act narrative.", input_variables=[], execution_settings={chat_service_id: act_narrative_exec_settings})
        kernel_instance.add_function(function_name="GenerateActNarrativeOnly", plugin_name=STORYTELLING_PLUGIN_NAME, prompt_template_config=act_narrative_prompt_config)
        logger.info(f"SK_SETUP: Registered GenerateActNarrativeOnly in {STORYTELLING_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering GenerateActNarrativeOnly: {e}", exc_info=True)

    # Act Metadata Generation
    try:
        act_metadata_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_metadata"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["act_metadata"], 
            top_p=settings.AI_TOP_P_SETTINGS["act_metadata"], 
            response_format={"type": "json_object"})
        act_metadata_prompt_config = PromptTemplateConfig(template=ACT_METADATA_GENERATION_PROMPT, name="GenerateActMetadata", template_format="semantic-kernel", description="Generates Act metadata.", input_variables=[], execution_settings={chat_service_id: act_metadata_exec_settings})
        kernel_instance.add_function(function_name="GenerateActMetadata", plugin_name=STORY_ANALYSIS_PLUGIN_NAME, prompt_template_config=act_metadata_prompt_config)
        logger.info(f"SK_SETUP: Registered GenerateActMetadata in {STORY_ANALYSIS_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering GenerateActMetadata: {e}", exc_info=True)

    # Scene Extraction from Act
    try:
        scene_extraction_exec_settings = AzureChatPromptExecutionSettings(service_id=chat_service_id, max_tokens=settings.SCENE_EXTRACTION_MAX_TOKENS, temperature=settings.SCENE_EXTRACTION_TEMPERATURE, top_p=settings.AI_TOP_P_SETTINGS["scene_extraction"])
        scene_extraction_prompt_config = PromptTemplateConfig(template=SCENE_EXTRACTION_SYSTEM_PROMPT, name="ExtractScenesFromAct", template_format="semantic-kernel", description="Extracts scenes from act content.", input_variables=[], execution_settings={chat_service_id: scene_extraction_exec_settings})
        kernel_instance.add_function(function_name="ExtractScenesFromAct", plugin_name=STORY_STRUCTURE_PLUGIN_NAME, prompt_template_config=scene_extraction_prompt_config)
        logger.info(f"SK_SETUP: Registered ExtractScenesFromAct in {STORY_STRUCTURE_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering ExtractScenesFromAct: {e}", exc_info=True)

    # Scene Narrative-Only Generation
    try:
        scene_narrative_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["scene_narrative"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["scene_narrative"], 
            top_p=settings.AI_TOP_P_SETTINGS["scene_narrative"])
        scene_narrative_prompt_config = PromptTemplateConfig(template=SCENE_NARRATIVE_ONLY_PROMPT, name="GenerateSceneNarrativeOnly", template_format="semantic-kernel", description="Generates scene narrative.", input_variables=[], execution_settings={chat_service_id: scene_narrative_exec_settings})
        kernel_instance.add_function(function_name="GenerateSceneNarrativeOnly", plugin_name=STORYTELLING_PLUGIN_NAME, prompt_template_config=scene_narrative_prompt_config)
        logger.info(f"SK_SETUP: Registered GenerateSceneNarrativeOnly in {STORYTELLING_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering GenerateSceneNarrativeOnly: {e}", exc_info=True)

    # Scene Metadata Generation
    try:
        scene_metadata_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["scene_metadata"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["scene_metadata"], 
            top_p=settings.AI_TOP_P_SETTINGS["scene_metadata"], 
            response_format={"type": "json_object"})
        scene_metadata_prompt_config = PromptTemplateConfig(template=SCENE_METADATA_GENERATION_PROMPT, name="GenerateSceneMetadata", template_format="semantic-kernel", description="Generates scene metadata.", input_variables=[], execution_settings={chat_service_id: scene_metadata_exec_settings})
        kernel_instance.add_function(function_name="GenerateSceneMetadata", plugin_name=STORY_ANALYSIS_PLUGIN_NAME, prompt_template_config=scene_metadata_prompt_config)
        logger.info(f"SK_SETUP: Registered GenerateSceneMetadata in {STORY_ANALYSIS_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering GenerateSceneMetadata: {e}", exc_info=True)

    # Documentizing World Elements
    rag_doc_exec_settings = AzureChatPromptExecutionSettings(
        service_id=chat_service_id, 
        max_tokens=settings.AI_MAX_TOKEN_SETTINGS["rag_conversion"], 
        temperature=settings.AI_TEMPERATURE_SETTINGS["rag_conversion"], 
        top_p=settings.AI_TOP_P_SETTINGS["rag_conversion"])
    try:
        char_to_rag_config = PromptTemplateConfig(template=CHARACTER_TO_RAG_TEXT_PROMPT, name="ConvertCharacterToRAGText", template_format="semantic-kernel", description="Converts character data to RAG text.", input_variables=[], execution_settings={chat_service_id: rag_doc_exec_settings})
        kernel_instance.add_function(function_name="ConvertCharacterToRAGText", plugin_name=WORLD_BUILDING_PLUGIN_NAME, prompt_template_config=char_to_rag_config)
        logger.info(f"SK_SETUP: Registered ConvertCharacterToRAGText in {WORLD_BUILDING_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering ConvertCharacterToRAGText: {e}", exc_info=True)
    try:
        loc_to_rag_config = PromptTemplateConfig(template=LOCATION_TO_RAG_TEXT_PROMPT, name="ConvertLocationToRAGText", template_format="semantic-kernel", description="Converts location data to RAG text.", input_variables=[], execution_settings={chat_service_id: rag_doc_exec_settings})
        kernel_instance.add_function(function_name="ConvertLocationToRAGText", plugin_name=WORLD_BUILDING_PLUGIN_NAME, prompt_template_config=loc_to_rag_config)
        logger.info(f"SK_SETUP: Registered ConvertLocationToRAGText in {WORLD_BUILDING_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering ConvertLocationToRAGText: {e}", exc_info=True)
    try:
        lore_to_rag_config = PromptTemplateConfig(template=LORE_ITEM_TO_RAG_TEXT_PROMPT, name="ConvertLoreItemToRAGText", template_format="semantic-kernel", description="Converts lore item data to RAG text.", input_variables=[], execution_settings={chat_service_id: rag_doc_exec_settings})
        kernel_instance.add_function(function_name="ConvertLoreItemToRAGText", plugin_name=WORLD_BUILDING_PLUGIN_NAME, prompt_template_config=lore_to_rag_config)
        logger.info(f"SK_SETUP: Registered ConvertLoreItemToRAGText in {WORLD_BUILDING_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering ConvertLoreItemToRAGText: {e}", exc_info=True)

    # World Generation from Book Title
    try:
        world_gen_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id, 
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["world_generation"], 
            temperature=settings.AI_TEMPERATURE_SETTINGS["world_generation"], 
            top_p=settings.AI_TOP_P_SETTINGS["world_generation"], 
            response_format={"type": "json_object"})
        world_gen_config = PromptTemplateConfig(template=GENERATE_WORLD_FROM_BOOK_PROMPT_TEXT, name="GenerateWorldFromBookTitle", template_format="semantic-kernel", description="Generates world definition from book title.", input_variables=[], execution_settings={chat_service_id: world_gen_exec_settings})
        kernel_instance.add_function(function_name="GenerateWorldFromBookTitle", plugin_name=WORLD_GENERATION_PLUGIN_NAME, prompt_template_config=world_gen_config)
        logger.info(f"SK_SETUP: Registered GenerateWorldFromBookTitle in {WORLD_GENERATION_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering GenerateWorldFromBookTitle: {e}", exc_info=True)

    # World Element Extraction from Text
    try:
        world_extract_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id,
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["world_elements_extraction"],
            temperature=settings.AI_TEMPERATURE_SETTINGS["world_elements_extraction"],
            top_p=settings.AI_TOP_P_SETTINGS["world_elements_extraction"],
            response_format={"type": "json_object"})
        world_extract_config = PromptTemplateConfig(template=EXTRACT_WORLD_ELEMENTS_FROM_TEXT_PROMPT, name="ExtractWorldElementsFromText", template_format="semantic-kernel", description="Extracts world elements from a block of text.", input_variables=[], execution_settings={chat_service_id: world_extract_exec_settings})
        kernel_instance.add_function(function_name="ExtractWorldElementsFromText", plugin_name=WORLD_GENERATION_PLUGIN_NAME, prompt_template_config=world_extract_config)
        logger.info(f"SK_SETUP: Registered ExtractWorldElementsFromText in {WORLD_GENERATION_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering ExtractWorldElementsFromText: {e}", exc_info=True)

    # Character Backstory Generation
    try:
        character_backstory_exec_settings = AzureChatPromptExecutionSettings(
            service_id=chat_service_id,
            max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_narrative"],
            temperature=settings.AI_TEMPERATURE_SETTINGS["act_narrative"],
            top_p=settings.AI_TOP_P_SETTINGS["act_narrative"])
        character_backstory_config = PromptTemplateConfig(template=CHARACTER_BACKSTORY_GENERATION_PROMPT, name="GenerateCharacterBackstory", template_format="semantic-kernel", description="Generates compelling character backstory.", input_variables=[], execution_settings={chat_service_id: character_backstory_exec_settings})
        kernel_instance.add_function(function_name="GenerateCharacterBackstory", plugin_name=WORLD_BUILDING_PLUGIN_NAME, prompt_template_config=character_backstory_config)
        logger.info(f"SK_SETUP: Registered GenerateCharacterBackstory in {WORLD_BUILDING_PLUGIN_NAME}.")
    except Exception as e: logger.error(f"SK_SETUP: ERROR registering GenerateCharacterBackstory: {e}", exc_info=True)

    # --- Register Basic Story Functions ---
    basic_story_exec_settings = AzureChatPromptExecutionSettings(
        service_id=chat_service_id,
        max_tokens=settings.AI_MAX_TOKEN_SETTINGS.get("creative_writing", 2000),
        temperature=settings.AI_TEMPERATURE_SETTINGS.get("creative_writing", 0.7),
        top_p=settings.AI_TOP_P_SETTINGS.get("creative_writing", 0.9))
    
    # Register all Basic Story prompts
    basic_story_prompts = [
        ("basic_writing_assistance", BASIC_WRITING_ASSISTANCE_PROMPT),
        ("continue_story", CONTINUE_STORY_PROMPT),
        ("what_happens_next", WHAT_HAPPENS_NEXT_PROMPT),
        ("improve_dialogue", IMPROVE_DIALOGUE_PROMPT),
        ("scene_development", SCENE_DEVELOPMENT_PROMPT),
        ("plot_brainstorm", PLOT_BRAINSTORM_PROMPT),
        ("writing_feedback", WRITING_FEEDBACK_PROMPT),
        ("creative_brainstorm", CREATIVE_BRAINSTORM_PROMPT),
        ("story_problem_solver", STORY_PROBLEM_SOLVER_PROMPT),
        ("character_voice_development", CHARACTER_VOICE_DEVELOPMENT_PROMPT),
        ("emotional_development", EMOTIONAL_DEVELOPMENT_PROMPT),
        ("basic_story_summary", BASIC_STORY_SUMMARY_PROMPT),
        ("basic_act_summary", BASIC_ACT_SUMMARY_PROMPT),
        ("basic_scene_summary", BASIC_SCENE_SUMMARY_PROMPT)
    ]
    
    for function_name, prompt_text in basic_story_prompts:
        try:
            prompt_config = PromptTemplateConfig(
                template=prompt_text,
                name=function_name,
                template_format="semantic-kernel",
                description=f"Basic Story: {function_name.replace('_', ' ').title()}",
                input_variables=[],
                execution_settings={chat_service_id: basic_story_exec_settings}
            )
            kernel_instance.add_function(
                function_name=function_name,
                plugin_name=BASIC_STORY_PLUGIN_NAME,
                prompt_template_config=prompt_config
            )
            logger.info(f"SK_SETUP: Registered {function_name} in {BASIC_STORY_PLUGIN_NAME}.")
        except Exception as e:
            logger.error(f"SK_SETUP: ERROR registering {function_name}: {e}", exc_info=True)

    # --- Register Story Brainstorm Plugin ---
    try:
        setup_story_brainstorm_plugin(kernel_instance, chat_service_id)
        logger.info("SK_SETUP: Story Brainstorm plugin setup completed.")
    except Exception as e:
        logger.error(f"SK_SETUP: ERROR setting up Story Brainstorm plugin: {e}", exc_info=True)

    logger.info("SK_SETUP: Semantic Kernel function registration attempts complete.")


initialize_kernel(kernel)

async def get_kernel():
    """Get the initialized kernel instance"""
    return kernel

review_act_content_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("ReviewActContentEnhanced")
generate_act_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateActNarrativeOnly")
generate_act_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateActMetadata")
generate_scene_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateSceneNarrativeOnly")
generate_scene_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateSceneMetadata")
retrieve_rag_context_function = kernel.plugins.get(RETRIEVAL_PLUGIN_NAME, {}).get("RetrieveRAGContext")
extract_scenes_from_act_function = kernel.plugins.get(STORY_STRUCTURE_PLUGIN_NAME, {}).get("ExtractScenesFromAct")
convert_character_to_rag_text_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("ConvertCharacterToRAGText")
convert_location_to_rag_text_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("ConvertLocationToRAGText")
convert_lore_item_to_rag_text_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("ConvertLoreItemToRAGText")
generate_world_from_book_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("GenerateWorldFromBookTitle")
extract_world_elements_from_text_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("ExtractWorldElementsFromText")
generate_character_backstory_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("GenerateCharacterBackstory")

# Story Brainstorm Plugin Functions
generate_story_concepts_function = kernel.plugins.get(STORY_BRAINSTORM_PLUGIN_NAME, {}).get("GenerateStoryConcepts")
generate_three_act_structure_function = kernel.plugins.get(STORY_BRAINSTORM_PLUGIN_NAME, {}).get("GenerateThreeActStructure")

_exported_functions_to_check = {
    "review_act_content_function": review_act_content_function,
    "generate_act_narrative_only_function": generate_act_narrative_only_function,
    "generate_act_metadata_function": generate_act_metadata_function,
    "generate_scene_narrative_only_function": generate_scene_narrative_only_function,
    "generate_scene_metadata_function": generate_scene_metadata_function,
    "retrieve_rag_context_function": retrieve_rag_context_function,
    "extract_scenes_from_act_function": extract_scenes_from_act_function,
    "convert_character_to_rag_text_function": convert_character_to_rag_text_function,
    "convert_location_to_rag_text_function": convert_location_to_rag_text_function,
    "convert_lore_item_to_rag_text_function": convert_lore_item_to_rag_text_function,
    "generate_world_from_book_function": generate_world_from_book_function,
    "extract_world_elements_from_text_function": extract_world_elements_from_text_function,
    "generate_character_backstory_function": generate_character_backstory_function,
    "generate_story_concepts_function": generate_story_concepts_function,
    "generate_three_act_structure_function": generate_three_act_structure_function,
}

logger.info("SK_KERNEL_INSTANCE: Checking exported function references:")
for name, func_ref in _exported_functions_to_check.items():
    if func_ref:
        logger.info(f"  [OK] Exported SK Function '{name}' is available.")
    else:
        logger.warning(f"  [WARNING] Exported SK Function '{name}' is NONE. This function will not be usable.")