"""Service helpers for semantic kernel setup."""

# /story_app/app/services/semantic_kernel_setup.py
#
# Semantic Kernel initialisation using OpenRouter (or any OpenAI-compatible provider).
# Replaces the previous cloud-specific setup with an OpenAI-compatible one.

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
import os
from typing import Optional
import logging
import openai

from app.core.config import settings
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
BASIC_STORY_PLUGIN_NAME = "basic_story"
STORY_BRAINSTORM_PLUGIN_NAME = "StoryBrainstormPlugin"


def load_prompt_from_file(filename: str) -> str:
    """Load prompt from file."""
    filepath = os.path.join(PROMPTS_DIR, filename)
    logger.debug(f"SK_SETUP: Loading prompt: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"SK_SETUP: Loaded prompt: {filepath}")
        return content
    except FileNotFoundError:
        logger.error(f"SK_SETUP: CRITICAL — Prompt file not found: {filepath}")
        raise RuntimeError(f"Essential prompt file missing: {filepath}")
    except Exception as e:
        logger.error(f"SK_SETUP: Error loading prompt {filepath}: {e}", exc_info=True)
        raise RuntimeError(f"Error loading prompt file {filepath}: {e}")


def load_basic_story_prompt_from_file(filename: str) -> str:
    """Load basic story prompt from file."""
    filepath = os.path.join(BASIC_STORY_PROMPTS_DIR, filename)
    logger.debug(f"SK_SETUP: Loading basic story prompt: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        logger.error(f"SK_SETUP: CRITICAL — Basic story prompt file not found: {filepath}")
        raise RuntimeError(f"Essential basic story prompt file missing: {filepath}")
    except Exception as e:
        logger.error(f"SK_SETUP: Error loading basic story prompt {filepath}: {e}", exc_info=True)
        raise RuntimeError(f"Error loading basic story prompt file {filepath}: {e}")


try:
    logger.info("SK_SETUP: Loading all system prompt files...")
    ENHANCED_ACT_REVIEW_PROMPT_TEXT = load_prompt_from_file("enhanced_act_review_prompt.txt")
    ACT_NARRATIVE_ONLY_PROMPT = load_prompt_from_file("generate_act_narrative_only.txt")
    ACT_METADATA_GENERATION_PROMPT = load_prompt_from_file("generate_act_metadata.txt")
    SCENE_NARRATIVE_ONLY_PROMPT = load_prompt_from_file("generate_scene_narrative_only.txt")
    SCENE_METADATA_GENERATION_PROMPT = load_prompt_from_file("generate_scene_metadata.txt")
    SCENE_EXTRACTION_SYSTEM_PROMPT = load_prompt_from_file("scene_extraction.txt")
    GENERATE_WORLD_FROM_BOOK_PROMPT_TEXT = load_prompt_from_file("generate_world_from_book.txt")
    CHARACTER_BACKSTORY_GENERATION_PROMPT = load_prompt_from_file("character_backstory_generation.txt")
    EXTRACT_WORLD_ELEMENTS_FROM_TEXT_PROMPT = load_prompt_from_file("extract_world_elements_from_text.txt")
    logger.info("SK_SETUP: All system prompt files loaded.")

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
    logger.info("SK_SETUP: All Basic Story prompt files loaded.")
except Exception as e_load_prompts:
    logger.critical(f"SK_SETUP: FAILED to load essential prompt files: {e_load_prompts}", exc_info=True)
    raise RuntimeError(f"Essential prompt files could not be loaded: {e_load_prompts}") from e_load_prompts


kernel = sk.Kernel()


def _build_openai_compatible_client() -> openai.AsyncOpenAI:
    """
    Build an AsyncOpenAI client pointed at the configured LLM provider.

    Priority:
      1. ACTIVE_LLM_PROVIDER=OPENROUTER → use OpenRouter
      2. ACTIVE_LLM_PROVIDER=OPENAI    → use OpenAI directly
      3. Any other provider            → raise
    """
    provider = settings.ACTIVE_LLM_PROVIDER.upper()

    if provider == "OPENROUTER":
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is not set. Cannot initialise Semantic Kernel.")
        headers = {}
        if settings.OPENROUTER_SITE_URL:
            headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            headers["X-Title"] = settings.OPENROUTER_APP_NAME
        return openai.AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers=headers or None,
        )

    if provider == "OPENAI":
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set. Cannot initialise Semantic Kernel.")
        return openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    raise RuntimeError(
        f"ACTIVE_LLM_PROVIDER='{provider}' is not supported for Semantic Kernel. "
        "Use OPENROUTER or OPENAI."
    )


def _resolve_model_id() -> str:
    """Return the model identifier for the default chat service."""
    provider = settings.ACTIVE_LLM_PROVIDER.upper()
    if provider == "OPENROUTER":
        return settings.OPENROUTER_DEFAULT_MODEL
    if provider == "OPENAI":
        return settings.DEFAULT_GENERATION_MODEL_NAME
    return settings.DEFAULT_GENERATION_MODEL_NAME


def initialize_kernel(kernel_instance: sk.Kernel) -> None:
    """Provide service support for initialize kernel."""
    logger.info("SK_SETUP: Initialising Semantic Kernel with OpenAI-compatible service...")

    chat_service_id = "chat_service"
    model_id = _resolve_model_id()

    try:
        async_client = _build_openai_compatible_client()
        kernel_instance.add_service(
            OpenAIChatCompletion(
                service_id=chat_service_id,
                ai_model_id=model_id,
                async_client=async_client,
            )
        )
        logger.info(f"SK_SETUP: Added OpenAIChatCompletion (service_id='{chat_service_id}', model='{model_id}')")
    except Exception as e:
        logger.critical(f"SK_SETUP: ERROR adding chat completion service: {e}", exc_info=True)
        return

    # Helper to build execution settings
    def _exec(max_tokens: int, temperature: float, top_p: float,
               response_format: Optional[dict] = None) -> OpenAIChatPromptExecutionSettings:
        kwargs = dict(
            service_id=chat_service_id,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        if response_format:
            kwargs["response_format"] = response_format
        return OpenAIChatPromptExecutionSettings(**kwargs)

    def _register(function_name: str, plugin_name: str, prompt: str,
                  exec_settings: OpenAIChatPromptExecutionSettings,
                  description: str = "") -> None:
        try:
            cfg = PromptTemplateConfig(
                template=prompt,
                name=function_name,
                template_format="semantic-kernel",
                description=description or function_name,
                input_variables=[],
                execution_settings={chat_service_id: exec_settings},
            )
            kernel_instance.add_function(
                function_name=function_name,
                plugin_name=plugin_name,
                prompt_template_config=cfg,
            )
            logger.info(f"SK_SETUP: Registered {plugin_name}.{function_name}")
        except Exception as e:
            logger.error(f"SK_SETUP: ERROR registering {plugin_name}.{function_name}: {e}", exc_info=True)

    t = settings.AI_TEMPERATURE_SETTINGS
    m = settings.AI_MAX_TOKEN_SETTINGS
    p = settings.AI_TOP_P_SETTINGS
    json_fmt = {"type": "json_object"}

    _register("ReviewActContentEnhanced", STORY_ANALYSIS_PLUGIN_NAME,
              ENHANCED_ACT_REVIEW_PROMPT_TEXT,
              _exec(m["act_review"], t["act_review"], p["act_review"], json_fmt))

    _register("GenerateActNarrativeOnly", STORYTELLING_PLUGIN_NAME,
              ACT_NARRATIVE_ONLY_PROMPT,
              _exec(m["act_narrative"], t["act_narrative"], p["act_narrative"]))

    _register("GenerateActMetadata", STORY_ANALYSIS_PLUGIN_NAME,
              ACT_METADATA_GENERATION_PROMPT,
              _exec(m["act_metadata"], t["act_metadata"], p["act_metadata"], json_fmt))

    _register("ExtractScenesFromAct", STORY_STRUCTURE_PLUGIN_NAME,
              SCENE_EXTRACTION_SYSTEM_PROMPT,
              _exec(settings.SCENE_EXTRACTION_MAX_TOKENS,
                    settings.SCENE_EXTRACTION_TEMPERATURE,
                    p["scene_extraction"]))

    _register("GenerateSceneNarrativeOnly", STORYTELLING_PLUGIN_NAME,
              SCENE_NARRATIVE_ONLY_PROMPT,
              _exec(m["scene_narrative"], t["scene_narrative"], p["scene_narrative"]))

    _register("GenerateSceneMetadata", STORY_ANALYSIS_PLUGIN_NAME,
              SCENE_METADATA_GENERATION_PROMPT,
              _exec(m["scene_metadata"], t["scene_metadata"], p["scene_metadata"], json_fmt))

    _register("GenerateWorldFromBookTitle", WORLD_GENERATION_PLUGIN_NAME,
              GENERATE_WORLD_FROM_BOOK_PROMPT_TEXT,
              _exec(m["world_generation"], t["world_generation"], p["world_generation"], json_fmt))

    _register("ExtractWorldElementsFromText", WORLD_GENERATION_PLUGIN_NAME,
              EXTRACT_WORLD_ELEMENTS_FROM_TEXT_PROMPT,
              _exec(m["world_elements_extraction"], t["world_elements_extraction"],
                    p["world_elements_extraction"], json_fmt))

    _register("GenerateCharacterBackstory", WORLD_BUILDING_PLUGIN_NAME,
              CHARACTER_BACKSTORY_GENERATION_PROMPT,
              _exec(m["act_narrative"], t["act_narrative"], p["act_narrative"]))

    # Basic Story prompts
    basic_exec = _exec(
        m.get("creative_writing", 2000),
        t.get("creative_writing", 0.7),
        p.get("creative_writing", 0.9),
    )
    for fn, prompt_text in [
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
        ("basic_scene_summary", BASIC_SCENE_SUMMARY_PROMPT),
    ]:
        _register(fn, BASIC_STORY_PLUGIN_NAME, prompt_text, basic_exec)

    try:
        setup_story_brainstorm_plugin(kernel_instance, chat_service_id)
        logger.info("SK_SETUP: Story Brainstorm plugin setup completed.")
    except Exception as e:
        logger.error(f"SK_SETUP: ERROR setting up Story Brainstorm plugin: {e}", exc_info=True)

    logger.info("SK_SETUP: Semantic Kernel function registration complete.")


initialize_kernel(kernel)


async def get_kernel():
    """Return the initialised kernel instance."""
    return kernel


review_act_content_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("ReviewActContentEnhanced")
generate_act_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateActNarrativeOnly")
generate_act_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateActMetadata")
generate_scene_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateSceneNarrativeOnly")
generate_scene_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateSceneMetadata")
extract_scenes_from_act_function = kernel.plugins.get(STORY_STRUCTURE_PLUGIN_NAME, {}).get("ExtractScenesFromAct")
generate_world_from_book_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("GenerateWorldFromBookTitle")
extract_world_elements_from_text_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("ExtractWorldElementsFromText")
generate_character_backstory_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("GenerateCharacterBackstory")
generate_story_concepts_function = kernel.plugins.get(STORY_BRAINSTORM_PLUGIN_NAME, {}).get("GenerateStoryConcepts")
generate_three_act_structure_function = kernel.plugins.get(STORY_BRAINSTORM_PLUGIN_NAME, {}).get("GenerateThreeActStructure")

_exported_functions_to_check = {
    "review_act_content_function": review_act_content_function,
    "generate_act_narrative_only_function": generate_act_narrative_only_function,
    "generate_act_metadata_function": generate_act_metadata_function,
    "generate_scene_narrative_only_function": generate_scene_narrative_only_function,
    "generate_scene_metadata_function": generate_scene_metadata_function,
    "extract_scenes_from_act_function": extract_scenes_from_act_function,
    "generate_world_from_book_function": generate_world_from_book_function,
    "extract_world_elements_from_text_function": extract_world_elements_from_text_function,
    "generate_character_backstory_function": generate_character_backstory_function,
    "generate_story_concepts_function": generate_story_concepts_function,
    "generate_three_act_structure_function": generate_three_act_structure_function,
}

logger.info("SK_KERNEL_INSTANCE: Checking exported function references:")
for name, func_ref in _exported_functions_to_check.items():
    if func_ref:
        logger.info(f"  [OK] '{name}' available.")
    else:
        logger.warning(f"  [WARNING] '{name}' is NONE — this function will not be usable.")

