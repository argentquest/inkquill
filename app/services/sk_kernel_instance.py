"""Compatibility layer for optional Semantic Kernel exports."""

import importlib
import logging
from types import SimpleNamespace

from app.services.ai_orchestration import (
    detect_optional_backends,
    get_ai_orchestration_backend,
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


def _load_semantic_kernel_setup():
    """Load the Semantic Kernel setup module only when explicitly enabled."""
    backend = get_ai_orchestration_backend()
    availability = detect_optional_backends()
    if not orchestration_backend_is_semantic_kernel():
        logger.info(
            "SK_KERNEL_INSTANCE: Semantic Kernel exports disabled because AI_ORCHESTRATION_BACKEND='%s'.",
            backend,
        )
        return _EMPTY_SETUP

    if not availability["semantic_kernel"]:
        logger.warning("SK_KERNEL_INSTANCE: semantic_kernel package is not installed; exports disabled.")
        return _EMPTY_SETUP

    try:
        from app.services import semantic_kernel_setup as semantic_kernel_setup

        logger.info("SK_KERNEL_INSTANCE: Semantic Kernel setup module loaded successfully.")
        return semantic_kernel_setup
    except Exception as exc:
        logger.exception("SK_KERNEL_INSTANCE: Failed to load Semantic Kernel setup; exports disabled: %s", exc)
        return _EMPTY_SETUP


_semantic_kernel_setup = _load_semantic_kernel_setup()


def _sync_exports() -> None:
    """Provide service support for sync exports."""
    global kernel
    global review_act_content_function, generate_act_narrative_only_function, generate_act_metadata_function
    global generate_scene_narrative_only_function, generate_scene_metadata_function
    global extract_scenes_from_act_function
    global generate_world_from_book_function, extract_world_elements_from_text_function
    global generate_character_backstory_function, generate_story_concepts_function, generate_three_act_structure_function
    global STORYTELLING_PLUGIN_NAME, STORY_ANALYSIS_PLUGIN_NAME, STORY_STRUCTURE_PLUGIN_NAME
    global WORLD_BUILDING_PLUGIN_NAME, WORLD_GENERATION_PLUGIN_NAME

    kernel = _semantic_kernel_setup.kernel
    review_act_content_function = _semantic_kernel_setup.review_act_content_function
    generate_act_narrative_only_function = _semantic_kernel_setup.generate_act_narrative_only_function
    generate_act_metadata_function = _semantic_kernel_setup.generate_act_metadata_function
    generate_scene_narrative_only_function = _semantic_kernel_setup.generate_scene_narrative_only_function
    generate_scene_metadata_function = _semantic_kernel_setup.generate_scene_metadata_function
    extract_scenes_from_act_function = _semantic_kernel_setup.extract_scenes_from_act_function
    generate_world_from_book_function = _semantic_kernel_setup.generate_world_from_book_function
    extract_world_elements_from_text_function = _semantic_kernel_setup.extract_world_elements_from_text_function
    generate_character_backstory_function = _semantic_kernel_setup.generate_character_backstory_function
    generate_story_concepts_function = _semantic_kernel_setup.generate_story_concepts_function
    generate_three_act_structure_function = _semantic_kernel_setup.generate_three_act_structure_function
    STORYTELLING_PLUGIN_NAME = _semantic_kernel_setup.STORYTELLING_PLUGIN_NAME
    STORY_ANALYSIS_PLUGIN_NAME = _semantic_kernel_setup.STORY_ANALYSIS_PLUGIN_NAME
    STORY_STRUCTURE_PLUGIN_NAME = _semantic_kernel_setup.STORY_STRUCTURE_PLUGIN_NAME
    WORLD_BUILDING_PLUGIN_NAME = _semantic_kernel_setup.WORLD_BUILDING_PLUGIN_NAME
    WORLD_GENERATION_PLUGIN_NAME = _semantic_kernel_setup.WORLD_GENERATION_PLUGIN_NAME


def reload_kernel():
    """Provide service support for reload kernel."""
    global _semantic_kernel_setup
    if _semantic_kernel_setup is _EMPTY_SETUP:
        logger.info("SK_KERNEL_INSTANCE: reload requested while Semantic Kernel is disabled; keeping empty exports.")
        return

    _semantic_kernel_setup = importlib.reload(_semantic_kernel_setup)
    _sync_exports()
    logger.info("SK_KERNEL_INSTANCE: Kernel reloaded using provider-neutral semantic_kernel_setup.")


_sync_exports()


