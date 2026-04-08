"""Primary storytelling runtime exports for app consumers."""

import importlib
import logging
from types import SimpleNamespace

from app.services.ai_orchestration import (
    detect_optional_backends,
    get_ai_orchestration_backend,
    orchestration_backend_is_langgraph,
    orchestration_backend_is_semantic_kernel,
)

logger = logging.getLogger(__name__)


_EMPTY_SETUP = SimpleNamespace(
    kernel=None,
    review_act_content_function=None,
    generate_act_narrative_only_function=None,
    generate_act_metadata_function=None,
    generate_scene_narrative_only_function=None,
    generate_scene_metadata_function=None,
    extract_scenes_from_act_function=None,
    generate_story_structure_function=None,
    generate_world_from_book_function=None,
    extract_world_elements_from_text_function=None,
    generate_character_backstory_function=None,
    generate_story_concepts_function=None,
    generate_three_act_structure_function=None,
    STORYTELLING_PLUGIN_NAME="StorytellingPlugin",
    STORY_ANALYSIS_PLUGIN_NAME="StoryAnalysisPlugin",
    STORY_STRUCTURE_PLUGIN_NAME="StoryStructurePlugin",
    WORLD_BUILDING_PLUGIN_NAME="WorldBuildingPlugin",
    WORLD_GENERATION_PLUGIN_NAME="WorldGenerationPlugin",
)


def _load_runtime_setup():
    """Load the active storytelling runtime exports."""
    backend = get_ai_orchestration_backend()
    availability = detect_optional_backends()
    if not (orchestration_backend_is_semantic_kernel() or orchestration_backend_is_langgraph()):
        logger.info(
            "STORYTELLING_RUNTIME: exports disabled because AI_ORCHESTRATION_BACKEND='%s'.",
            backend,
        )
        return _EMPTY_SETUP

    if not availability["langgraph"] or not availability["langchain_openai"]:
        logger.warning("STORYTELLING_RUNTIME: LangGraph runtime dependencies are unavailable; exports disabled.")
        return _EMPTY_SETUP

    try:
        from app.services import langgraph_runtime_setup

        logger.info("STORYTELLING_RUNTIME: runtime module loaded successfully for backend '%s'.", backend)
        return langgraph_runtime_setup
    except Exception as exc:
        logger.exception("STORYTELLING_RUNTIME: Failed to load storytelling runtime exports: %s", exc)
        return _EMPTY_SETUP


_runtime_setup = _load_runtime_setup()


def _sync_exports() -> None:
    """Provide service support for sync exports."""
    global kernel
    global review_act_content_function, generate_act_narrative_only_function, generate_act_metadata_function
    global generate_scene_narrative_only_function, generate_scene_metadata_function
    global extract_scenes_from_act_function, generate_story_structure_function
    global generate_world_from_book_function, extract_world_elements_from_text_function
    global generate_character_backstory_function, generate_story_concepts_function, generate_three_act_structure_function
    global STORYTELLING_PLUGIN_NAME, STORY_ANALYSIS_PLUGIN_NAME, STORY_STRUCTURE_PLUGIN_NAME
    global WORLD_BUILDING_PLUGIN_NAME, WORLD_GENERATION_PLUGIN_NAME

    kernel = _runtime_setup.kernel
    review_act_content_function = _runtime_setup.review_act_content_function
    generate_act_narrative_only_function = _runtime_setup.generate_act_narrative_only_function
    generate_act_metadata_function = _runtime_setup.generate_act_metadata_function
    generate_scene_narrative_only_function = _runtime_setup.generate_scene_narrative_only_function
    generate_scene_metadata_function = _runtime_setup.generate_scene_metadata_function
    extract_scenes_from_act_function = _runtime_setup.extract_scenes_from_act_function
    generate_story_structure_function = _runtime_setup.generate_story_structure_function
    generate_world_from_book_function = _runtime_setup.generate_world_from_book_function
    extract_world_elements_from_text_function = _runtime_setup.extract_world_elements_from_text_function
    generate_character_backstory_function = _runtime_setup.generate_character_backstory_function
    generate_story_concepts_function = _runtime_setup.generate_story_concepts_function
    generate_three_act_structure_function = _runtime_setup.generate_three_act_structure_function
    STORYTELLING_PLUGIN_NAME = _runtime_setup.STORYTELLING_PLUGIN_NAME
    STORY_ANALYSIS_PLUGIN_NAME = _runtime_setup.STORY_ANALYSIS_PLUGIN_NAME
    STORY_STRUCTURE_PLUGIN_NAME = _runtime_setup.STORY_STRUCTURE_PLUGIN_NAME
    WORLD_BUILDING_PLUGIN_NAME = _runtime_setup.WORLD_BUILDING_PLUGIN_NAME
    WORLD_GENERATION_PLUGIN_NAME = _runtime_setup.WORLD_GENERATION_PLUGIN_NAME


def reload_kernel():
    """Provide service support for reload kernel."""
    global _runtime_setup
    if _runtime_setup is _EMPTY_SETUP:
        logger.info("STORYTELLING_RUNTIME: reload requested while exports are disabled; keeping empty exports.")
        return

    _runtime_setup = importlib.reload(_runtime_setup)
    _sync_exports()
    logger.info("STORYTELLING_RUNTIME: Runtime exports reloaded successfully.")


_sync_exports()


