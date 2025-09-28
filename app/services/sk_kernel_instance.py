# /ai_rag_story_app/app/services/sk_kernel_instance.py
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
import logging
import os

from app.core.config import settings
from .rag_retrieval import RetrievalPlugin 

from .sk_plugins import (
    story_analysis_plugin_setup,
    storytelling_plugin_setup,
    story_structure_plugin_setup,
    world_building_plugin_setup,
    world_generation_plugin_setup
)

from app.services.sk_constants import (
    STORYTELLING_PLUGIN_NAME,
    STORY_ANALYSIS_PLUGIN_NAME,
    STORY_STRUCTURE_PLUGIN_NAME,
    WORLD_BUILDING_PLUGIN_NAME,
    WORLD_GENERATION_PLUGIN_NAME,
    RETRIEVAL_PLUGIN_NAME
)

logger = logging.getLogger(__name__)

kernel = sk.Kernel()

_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_SYSTEM_DIR = os.path.join(_SERVICE_DIR, '..', 'prompts', 'system')

def load_prompt_from_file_global(filename: str) -> str:
    filepath = os.path.join(PROMPTS_SYSTEM_DIR, filename)
    logger.debug(f"SK_GLOBAL_LOAD: Attempting to load prompt file: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"SK_GLOBAL_LOAD: Successfully loaded prompt from: {filepath}")
        return content
    except FileNotFoundError:
        logger.error(f"SK_GLOBAL_LOAD: CRITICAL - Prompt file {filepath} not found.")
        raise RuntimeError(f"Essential prompt file missing: {filepath}")
    except Exception as e:
        logger.error(f"SK_GLOBAL_LOAD: Error loading prompt file {filepath}: {e}", exc_info=True)
        raise RuntimeError(f"Error loading prompt file {filepath}: {e}")


def reload_kernel():
    """Reload the kernel by re-initializing all services and plugins."""
    global kernel
    kernel = sk.Kernel()
    _initialize_sk_services_and_plugins()
    _update_exported_functions()
    _check_exported_functions()
    logger.info("SK_KERNEL_INSTANCE: Kernel reloaded successfully")

def _initialize_sk_services_and_plugins():
    logger.info("SK_KERNEL_INSTANCE: Initializing Semantic Kernel with services and plugins...")
    
    azure_openai_endpoint = str(settings.AZURE_OPENAI_ENDPOINT) if settings.AZURE_OPENAI_ENDPOINT else None
    azure_openai_api_key = settings.AZURE_OPENAI_API_KEY
    azure_openai_api_version = settings.AZURE_OPENAI_API_VERSION
    
    # --- BEGIN FIX: Use the new _DEFAULT setting name ---
    # This ensures the kernel initializes with a valid chat deployment name.
    # The dynamic selection will happen later in the WebSocket handlers.
    chat_deployment_name = settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT
    # --- END FIX ---

    embedding_deployment_name = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    
    chat_service_id = "azure_openai_chat_service"
    embedding_service_id = "azure_openai_embedding_service"

    if not all([azure_openai_endpoint, azure_openai_api_key, chat_deployment_name]):
        logger.critical("SK_KERNEL_INSTANCE: Azure OpenAI CHAT configuration incomplete. SK chat features will likely fail.")
    else:
        try:
            kernel.add_service(AzureChatCompletion(
                service_id=chat_service_id, 
                deployment_name=chat_deployment_name, 
                endpoint=azure_openai_endpoint,
                api_key=azure_openai_api_key, 
                api_version=azure_openai_api_version
            ))
            logger.info(f"SK_KERNEL_INSTANCE: Added AzureChatCompletion service (ID: {chat_service_id}, Deployment: {chat_deployment_name})")
        except Exception as e:
            logger.error(f"SK_KERNEL_INSTANCE: ERROR adding AzureChatCompletion service: {e}", exc_info=True)

    if all([azure_openai_endpoint, azure_openai_api_key, embedding_deployment_name]):
        try:
            kernel.add_service(AzureTextEmbedding(
                service_id=embedding_service_id, 
                deployment_name=embedding_deployment_name, 
                endpoint=azure_openai_endpoint,
                api_key=azure_openai_api_key, 
                api_version=azure_openai_api_version
            ))
            logger.info(f"SK_KERNEL_INSTANCE: Added AzureTextEmbedding service (ID: {embedding_service_id}, Deployment: {embedding_deployment_name})")
        except Exception as e:
            logger.error(f"SK_KERNEL_INSTANCE: ERROR adding AzureTextEmbedding service: {e}", exc_info=True)
    else:
        logger.warning("SK_KERNEL_INSTANCE: Azure OpenAI EMBEDDING configuration incomplete. Embedding features may fail or be unavailable.")

    try:
        kernel.add_plugin(RetrievalPlugin(), plugin_name=RETRIEVAL_PLUGIN_NAME)
        logger.info(f"SK_KERNEL_INSTANCE: Registered native plugin '{RETRIEVAL_PLUGIN_NAME}'.")
    except Exception as e:
        logger.error(f"SK_KERNEL_INSTANCE: ERROR registering native plugin '{RETRIEVAL_PLUGIN_NAME}': {e}", exc_info=True)

    story_analysis_plugin_setup.register_story_analysis_functions(kernel, chat_service_id, load_prompt_from_file_global)
    storytelling_plugin_setup.register_storytelling_functions(kernel, chat_service_id, load_prompt_from_file_global)
    story_structure_plugin_setup.register_story_structure_functions(kernel, chat_service_id, load_prompt_from_file_global)
    world_building_plugin_setup.register_world_building_functions(kernel, chat_service_id, load_prompt_from_file_global)
    world_generation_plugin_setup.register_world_generation_functions(kernel, chat_service_id, load_prompt_from_file_global)
    
    logger.info("SK_KERNEL_INSTANCE: All plugin registration attempts complete.")

def _update_exported_functions():
    """Update exported function references after kernel initialization."""
    global review_act_content_function, generate_act_narrative_only_function, generate_act_metadata_function
    global generate_scene_narrative_only_function, generate_scene_metadata_function, retrieve_rag_context_function
    global extract_scenes_from_act_function, generate_story_structure_function, convert_character_to_rag_text_function
    global convert_location_to_rag_text_function, convert_lore_item_to_rag_text_function, generate_world_from_book_function
    global extract_world_elements_from_text_function, generate_character_backstory_function
    
    review_act_content_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("ReviewActContentEnhanced")
    generate_act_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateActNarrativeOnly")
    generate_act_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateActMetadata")
    generate_scene_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateSceneNarrativeOnly")
    generate_scene_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateSceneMetadata")
    retrieve_rag_context_function = kernel.plugins.get(RETRIEVAL_PLUGIN_NAME, {}).get("RetrieveRAGContext")
    extract_scenes_from_act_function = kernel.plugins.get(STORY_STRUCTURE_PLUGIN_NAME, {}).get("ExtractScenesFromAct")
    generate_story_structure_function = kernel.plugins.get(STORY_STRUCTURE_PLUGIN_NAME, {}).get("GenerateStoryStructure")
    convert_character_to_rag_text_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("ConvertCharacterToRAGText")
    convert_location_to_rag_text_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("ConvertLocationToRAGText")
    convert_lore_item_to_rag_text_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("ConvertLoreItemToRAGText")
    generate_world_from_book_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("GenerateWorldFromBookTitle")
    extract_world_elements_from_text_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("ExtractWorldElementsFromText")
    generate_character_backstory_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("GenerateCharacterBackstory")

# Exported function references for use in other parts of the application
review_act_content_function = None
generate_act_narrative_only_function = None
generate_act_metadata_function = None
generate_scene_narrative_only_function = None
generate_scene_metadata_function = None
retrieve_rag_context_function = None
extract_scenes_from_act_function = None
generate_story_structure_function = None
convert_character_to_rag_text_function = None
convert_location_to_rag_text_function = None
convert_lore_item_to_rag_text_function = None
generate_world_from_book_function = None
extract_world_elements_from_text_function = None
generate_character_backstory_function = None

def _check_exported_functions():
    """Check and log the status of exported function references."""
    _exported_functions_to_check = {
        "review_act_content_function": review_act_content_function,
        "generate_act_narrative_only_function": generate_act_narrative_only_function,
        "generate_act_metadata_function": generate_act_metadata_function,
        "generate_scene_narrative_only_function": generate_scene_narrative_only_function,
        "generate_scene_metadata_function": generate_scene_metadata_function,
        "retrieve_rag_context_function": retrieve_rag_context_function,
        "extract_scenes_from_act_function": extract_scenes_from_act_function,
        "generate_story_structure_function": generate_story_structure_function,
        "convert_character_to_rag_text_function": convert_character_to_rag_text_function,
        "convert_location_to_rag_text_function": convert_location_to_rag_text_function,
        "convert_lore_item_to_rag_text_function": convert_lore_item_to_rag_text_function,
        "generate_world_from_book_function": generate_world_from_book_function,
        "extract_world_elements_from_text_function": extract_world_elements_from_text_function,
        "generate_character_backstory_function": generate_character_backstory_function,
    }
    
    logger.info("SK_KERNEL_INSTANCE: Checking exported function references:")
    for name, func_ref in _exported_functions_to_check.items():
        if func_ref:
            logger.info(f"  [OK] Exported SK Function '{name}' is available.")
        else:
            logger.warning(f"  [WARNING] Exported SK Function '{name}' is NONE. This function will not be usable.")

# Initialize the kernel instance and all its functions when this module is imported.
_initialize_sk_services_and_plugins()
_update_exported_functions()
_check_exported_functions()

