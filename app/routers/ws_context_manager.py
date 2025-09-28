# /ai_rag_story_app/app/routers/ws_context_manager.py
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from markdownify import markdownify as md

from app.crud import story as crud_story, act as crud_act, scene as crud_scene
from app.crud import character as crud_character, location as crud_location, lore_item as crud_lore_item
from app.models.act import Act
from app.models.scene import Scene

logger = logging.getLogger(__name__)

class ContextNotFoundError(Exception):
    """Custom exception for when essential context (story, act, etc.) is not found or accessible."""
    pass

def _format_linked_elements_for_prompt(
    elements: List[Dict[str, Any]],
    element_type_name: str,
    name_field: str,
    role_field: str,
    desc_field: str = "description",
    max_elements: int = 7
) -> str:
    """Formats a list of linked elements into a string suitable for an AI prompt."""
    if not elements:
        return f"No specific {element_type_name}s are explicitly linked to this story."
    
    formatted_list = []
    for i, el_dict in enumerate(elements):
        if i >= max_elements:
            formatted_list.append(f"- ...and {len(elements) - max_elements} more.")
            break
        
        name = el_dict.get(name_field, "Unnamed Element")
        role = el_dict.get(role_field, "Role/relevance not specified.")
        description = el_dict.get(desc_field, "") or ""
        desc_snippet = f" (Desc: {description.strip()[:75]}...)" if description.strip() else ""
        
        # Add AI import fields if available (check if they're in the dict)
        additional_info = []
        if el_dict.get('relationships'):
            additional_info.append(f"Relationships: {el_dict['relationships'][:50]}...")
        if el_dict.get('geography'):
            additional_info.append(f"Geography: {el_dict['geography'][:50]}...")
        if el_dict.get('cultural_context'):
            additional_info.append(f"Culture: {el_dict['cultural_context'][:50]}...")
        if el_dict.get('connected_elements'):
            additional_info.append(f"Connections: {el_dict['connected_elements'][:50]}...")
        if el_dict.get('related_elements'):
            additional_info.append(f"Related: {el_dict['related_elements'][:50]}...")
        
        additional_context = f" [{', '.join(additional_info)}]" if additional_info else ""
        formatted_list.append(f"- {name} (Role/Relevance: {role}){desc_snippet}{additional_context}")
        
    return f"Key {element_type_name}s for this Story:\n" + "\n".join(formatted_list)


async def get_narrative_generation_context(
    db: AsyncSession,
    user_id: int,
    story_id: int,
    act_id: int,
    scene_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Fetches and formats all necessary context for an AI narrative generation request.
    This includes story, act, scene, previous scenes/acts, and linked world elements.
    """
    context_dict: Dict[str, Any] = {}

    story_obj = await crud_story.get_story_for_user(db, story_id=story_id, user_id=user_id)
    if not story_obj:
        raise ContextNotFoundError(f"Story {story_id} not found or not owned by user {user_id}.")
    
    context_dict["story_title"] = story_obj.title
    context_dict["story_description"] = story_obj.short_description or "No story summary provided."

    parent_act_obj = await crud_act.get_act(db, act_id=act_id)
    if not parent_act_obj or parent_act_obj.story_id != story_id:
        raise ContextNotFoundError(f"Act {act_id} not found or not part of story {story_id}.")

    context_dict["parent_act_number"] = str(parent_act_obj.act_number)
    context_dict["parent_act_title"] = parent_act_obj.title
    context_dict["parent_act_summary"] = parent_act_obj.act_summary or "No summary provided for the parent act."

    # Fetch previous acts summary
    if parent_act_obj.act_number > 1:
        stmt_prev_acts = select(Act.act_number, Act.title, Act.act_summary).where(
            Act.story_id == story_id, Act.act_number < parent_act_obj.act_number
        ).order_by(Act.act_number.asc())
        prev_acts_results = await db.execute(stmt_prev_acts)
        prev_acts_data_list = [
            f"  - Act {pa.act_number} ('{pa.title or 'Untitled'}'): {pa.act_summary or 'No summary.'}"
            for pa in prev_acts_results.mappings().all()
        ]
        context_dict["previous_acts_summaries"] = "Summaries of Previous Acts:\n" + "\n".join(prev_acts_data_list) if prev_acts_data_list else "No previous acts found."
    else:
        context_dict["previous_acts_summaries"] = "This is the first act."

    # Fetch linked world elements
    if story_obj.world_id:
        chars = await crud_character.get_characters_for_story(db, story_id=story_obj.id)
        context_dict["linked_characters_context"] = _format_linked_elements_for_prompt(chars, "Character", "name", "role_in_story")
        locs = await crud_location.get_locations_for_story(db, story_id=story_obj.id)
        context_dict["linked_locations_context"] = _format_linked_elements_for_prompt(locs, "Location", "name", "significance_to_story")
        lore = await crud_lore_item.get_lore_items_for_story(db, story_id=story_obj.id)
        context_dict["linked_lore_items_context"] = _format_linked_elements_for_prompt(lore, "Lore Item", "title", "relevance_to_story", "description")
    else:
        context_dict["linked_characters_context"] = "Story not linked to a world."
        context_dict["linked_locations_context"] = "Story not linked to a world."
        context_dict["linked_lore_items_context"] = "Story not linked to a world."

    # Scene-specific context
    if scene_id:
        current_scene_obj = await crud_scene.get_scene(db, scene_id=scene_id)
        if not current_scene_obj or current_scene_obj.act_id != act_id:
            raise ContextNotFoundError(f"Scene {scene_id} not found or not part of act {act_id}.")
        
        context_dict["scene_number"] = str(current_scene_obj.scene_number)
        context_dict["scene_title"] = current_scene_obj.title or "Untitled Scene"
        context_dict["current_scene_summary"] = current_scene_obj.summary or "Not specified."
        
        # Previous scenes in the same act
        if current_scene_obj.scene_number > 10:
            stmt_prev_scenes = select(Scene).where(Scene.act_id == act_id, Scene.scene_number < current_scene_obj.scene_number).order_by(Scene.scene_number.asc())
            prev_scenes_list = (await db.execute(stmt_prev_scenes)).scalars().all()
            formatted_scenes = [
                f"--- Previous Scene {ps.scene_number} ({ps.title or 'Untitled'}) ---\n{md(ps.content) if ps.content else '(No content)'}"
                for ps in prev_scenes_list
            ]
            context_dict["previous_scenes_full_content_in_act"] = "\n\n".join(formatted_scenes) if formatted_scenes else "No preceding scenes in this act."
        else:
            context_dict["previous_scenes_full_content_in_act"] = "This is the first scene in the act."

    logger.info(f"Successfully gathered narrative context for Story:{story_id}, Act:{act_id}, Scene:{scene_id or 'N/A'}")
    return context_dict