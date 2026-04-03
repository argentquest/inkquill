"""Service helpers for sk kernel instance."""

# /story_app/app/services/sk_kernel_instance.py
import importlib
import logging

from app.services import semantic_kernel_setup as _semantic_kernel_setup

logger = logging.getLogger(__name__)


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
    _semantic_kernel_setup = importlib.reload(_semantic_kernel_setup)
    _sync_exports()
    logger.info("SK_KERNEL_INSTANCE: Kernel reloaded using provider-neutral semantic_kernel_setup.")


_sync_exports()


