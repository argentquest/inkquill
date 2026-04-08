"""LangGraph-backed prompt registration for legacy storytelling flows."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.services.langgraph_kernel import (
    LangGraphKernel,
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
    PromptTemplateConfig,
    load_prompt_from_file as load_prompt_text,
)
from .sk_plugins.story_brainstorm_plugin_setup import setup_story_brainstorm_plugin

logger = logging.getLogger(__name__)

_CURRENT_FILE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = _CURRENT_FILE_DIR.parent / "prompts" / "system"
BASIC_STORY_PROMPTS_DIR = _CURRENT_FILE_DIR.parent / "prompts" / "basic_story"

STORYTELLING_PLUGIN_NAME = "StorytellingPlugin"
STORY_ANALYSIS_PLUGIN_NAME = "StoryAnalysisPlugin"
STORY_STRUCTURE_PLUGIN_NAME = "StoryStructurePlugin"
WORLD_BUILDING_PLUGIN_NAME = "WorldBuildingPlugin"
WORLD_GENERATION_PLUGIN_NAME = "WorldGenerationPlugin"
BASIC_STORY_PLUGIN_NAME = "basic_story"
STORY_BRAINSTORM_PLUGIN_NAME = "StoryBrainstormPlugin"


def load_prompt_from_file(filename: str) -> str:
    """Load prompt text from the system prompt directory."""
    prompt = load_prompt_text(PROMPTS_DIR, filename)
    logger.info("LANGGRAPH_SETUP: Loaded prompt: %s", PROMPTS_DIR / filename)
    return prompt


def load_basic_story_prompt_from_file(filename: str) -> str:
    """Load prompt text from the basic story prompt directory."""
    prompt = load_prompt_text(BASIC_STORY_PROMPTS_DIR, filename)
    logger.info("LANGGRAPH_SETUP: Loaded basic story prompt: %s", BASIC_STORY_PROMPTS_DIR / filename)
    return prompt


logger.info("LANGGRAPH_SETUP: Loading storytelling prompt files...")
ENHANCED_ACT_REVIEW_PROMPT_TEXT = load_prompt_from_file("enhanced_act_review_prompt.txt")
ACT_NARRATIVE_ONLY_PROMPT = load_prompt_from_file("generate_act_narrative_only.txt")
ACT_METADATA_GENERATION_PROMPT = load_prompt_from_file("generate_act_metadata.txt")
SCENE_NARRATIVE_ONLY_PROMPT = load_prompt_from_file("generate_scene_narrative_only.txt")
SCENE_METADATA_GENERATION_PROMPT = load_prompt_from_file("generate_scene_metadata.txt")
SCENE_EXTRACTION_SYSTEM_PROMPT = load_prompt_from_file("scene_extraction.txt")
TEXT_SUMMARY_PROMPT = load_prompt_from_file("generate_text_summary.txt")
STORY_STRUCTURE_GENERATION_PROMPT = load_prompt_from_file("story_generation.txt")
GENERATE_WORLD_FROM_BOOK_PROMPT_TEXT = load_prompt_from_file("generate_world_from_book.txt")
CHARACTER_BACKSTORY_GENERATION_PROMPT = load_prompt_from_file("character_backstory_generation.txt")
EXTRACT_WORLD_ELEMENTS_FROM_TEXT_PROMPT = load_prompt_from_file("extract_world_elements_from_text.txt")

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

kernel = LangGraphKernel()


def _resolve_model_id() -> str:
    provider = settings.ACTIVE_LLM_PROVIDER.upper()
    if provider == "OPENROUTER":
        return settings.OPENROUTER_DEFAULT_MODEL
    return settings.DEFAULT_GENERATION_MODEL_NAME


def initialize_kernel(kernel_instance: LangGraphKernel) -> None:
    """Register prompt functions against the LangGraph runtime."""
    chat_service_id = "chat_service"
    model_id = _resolve_model_id()
    kernel_instance.add_service(OpenAIChatCompletion(service_id=chat_service_id, ai_model_id=model_id))

    def _exec(max_tokens: int, temperature: float, top_p: float, response_format: Optional[dict] = None) -> OpenAIChatPromptExecutionSettings:
        return OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id,
            ai_model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            response_format=response_format,
        )

    def _register(function_name: str, plugin_name: str, prompt: str, exec_settings: OpenAIChatPromptExecutionSettings, description: str = "") -> None:
        prompt_config = PromptTemplateConfig(
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
            prompt_template_config=prompt_config,
        )
        logger.info("LANGGRAPH_SETUP: Registered %s.%s", plugin_name, function_name)

    t = settings.AI_TEMPERATURE_SETTINGS
    m = settings.AI_MAX_TOKEN_SETTINGS
    p = settings.AI_TOP_P_SETTINGS
    json_fmt = {"type": "json_object"}

    _register("ReviewActContentEnhanced", STORY_ANALYSIS_PLUGIN_NAME, ENHANCED_ACT_REVIEW_PROMPT_TEXT, _exec(m["act_review"], t["act_review"], p["act_review"], json_fmt))
    _register("GenerateActNarrativeOnly", STORYTELLING_PLUGIN_NAME, ACT_NARRATIVE_ONLY_PROMPT, _exec(m["act_narrative"], t["act_narrative"], p["act_narrative"]))
    _register("GenerateActMetadata", STORY_ANALYSIS_PLUGIN_NAME, ACT_METADATA_GENERATION_PROMPT, _exec(m["act_metadata"], t["act_metadata"], p["act_metadata"], json_fmt))
    _register("GenerateTextSummary", STORY_ANALYSIS_PLUGIN_NAME, TEXT_SUMMARY_PROMPT, _exec(m["scene_metadata"], t["scene_metadata"], p["scene_metadata"]))
    _register("ExtractScenesFromAct", STORY_STRUCTURE_PLUGIN_NAME, SCENE_EXTRACTION_SYSTEM_PROMPT, _exec(settings.SCENE_EXTRACTION_MAX_TOKENS, settings.SCENE_EXTRACTION_TEMPERATURE, p["scene_extraction"]))
    _register("GenerateStoryStructure", STORY_STRUCTURE_PLUGIN_NAME, STORY_STRUCTURE_GENERATION_PROMPT, _exec(m["story_generation"], t["story_generation"], p["story_generation"], json_fmt))
    _register("GenerateSceneNarrativeOnly", STORYTELLING_PLUGIN_NAME, SCENE_NARRATIVE_ONLY_PROMPT, _exec(m["scene_narrative"], t["scene_narrative"], p["scene_narrative"]))
    _register("GenerateSceneMetadata", STORY_ANALYSIS_PLUGIN_NAME, SCENE_METADATA_GENERATION_PROMPT, _exec(m["scene_metadata"], t["scene_metadata"], p["scene_metadata"], json_fmt))
    _register("GenerateWorldFromBookTitle", WORLD_GENERATION_PLUGIN_NAME, GENERATE_WORLD_FROM_BOOK_PROMPT_TEXT, _exec(m["world_generation"], t["world_generation"], p["world_generation"], json_fmt))
    _register("ExtractWorldElementsFromText", WORLD_GENERATION_PLUGIN_NAME, EXTRACT_WORLD_ELEMENTS_FROM_TEXT_PROMPT, _exec(m["world_elements_extraction"], t["world_elements_extraction"], p["world_elements_extraction"], json_fmt))
    _register("GenerateCharacterBackstory", WORLD_BUILDING_PLUGIN_NAME, CHARACTER_BACKSTORY_GENERATION_PROMPT, _exec(m["act_narrative"], t["act_narrative"], p["act_narrative"]))

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

    setup_story_brainstorm_plugin(kernel_instance, chat_service_id)


initialize_kernel(kernel)


async def get_kernel():
    """Return the initialized runtime."""
    return kernel


review_act_content_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("ReviewActContentEnhanced")
generate_act_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateActNarrativeOnly")
generate_act_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateActMetadata")
generate_scene_narrative_only_function = kernel.plugins.get(STORYTELLING_PLUGIN_NAME, {}).get("GenerateSceneNarrativeOnly")
generate_scene_metadata_function = kernel.plugins.get(STORY_ANALYSIS_PLUGIN_NAME, {}).get("GenerateSceneMetadata")
extract_scenes_from_act_function = kernel.plugins.get(STORY_STRUCTURE_PLUGIN_NAME, {}).get("ExtractScenesFromAct")
generate_story_structure_function = kernel.plugins.get(STORY_STRUCTURE_PLUGIN_NAME, {}).get("GenerateStoryStructure")
generate_world_from_book_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("GenerateWorldFromBookTitle")
extract_world_elements_from_text_function = kernel.plugins.get(WORLD_GENERATION_PLUGIN_NAME, {}).get("ExtractWorldElementsFromText")
generate_character_backstory_function = kernel.plugins.get(WORLD_BUILDING_PLUGIN_NAME, {}).get("GenerateCharacterBackstory")
generate_story_concepts_function = kernel.plugins.get(STORY_BRAINSTORM_PLUGIN_NAME, {}).get("GenerateStoryConcepts")
generate_three_act_structure_function = kernel.plugins.get(STORY_BRAINSTORM_PLUGIN_NAME, {}).get("GenerateThreeActStructure")
