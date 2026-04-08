"""Service helpers for story generation service."""

# /story_app/app/services/story_generation_service.py

import json
import logging
import re
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.world import World
from app.models.story import Story
from app.models.act import Act
from app.models.scene import Scene
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.ai_model_config import AIModelConfiguration
from app.schemas.story_generation import StoryGenerationRequest, StoryGenerationResponse
from app.crud import story as crud_story
from app.crud import act as crud_act
from app.crud import scene as crud_scene
from app.crud import ai_model_config as crud_ai_model_config
from app.services.cost_tracker_service import CostTrackerService
from app.services.ai_model_cache import model_cache

logger = logging.getLogger(__name__)

class StoryGenerationService:
    """Service for generating complete story structures using AI."""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        self.cost_tracker = CostTrackerService(db)
    
    async def generate_story_from_world(self, world: World, request: StoryGenerationRequest) -> StoryGenerationResponse:
        """
        Generate a complete story structure from world elements.
        
        Args:
            world: The world containing the elements
            request: The story generation request parameters
            
        Returns:
            StoryGenerationResponse with the generated story details
        """
        logger.info(f"Starting story generation for world '{world.name}' with {len(request.selected_characters)} characters, {len(request.selected_locations)} locations, {len(request.selected_lore_items)} lore items")
        
        try:
            # 1. Validate and fetch selected elements
            elements = await self._fetch_and_validate_elements(world, request)
            if not elements:
                return StoryGenerationResponse(
                    success=False,
                    error="Failed to validate selected world elements",
                    message="Please ensure all selected elements exist and belong to this world."
                )
            
            # Store elements for later use in associations
            self._elements_map = elements
            
            # 2. Get AI model configuration
            ai_model_config = await self._get_ai_model_config(request.ai_model_config_id)
            if not ai_model_config:
                return StoryGenerationResponse(
                    success=False,
                    error="Invalid AI model configuration",
                    message="The selected AI model is not available."
                )
            
            # 3. Generate story outline using AI
            outline_result = await self._generate_story_outline(world, elements, request, ai_model_config)
            if not outline_result["success"]:
                return StoryGenerationResponse(
                    success=False,
                    error=outline_result["error"],
                    partial_data=outline_result.get("partial_data"),
                    message="AI story generation failed. Please try again."
                )
            
            # 4. Create story structure in database
            story_result = await self._create_story_structure(
                world, 
                outline_result["outline"], 
                request
            )
            
            # 5. Create story-level associations for all used elements
            if story_result["success"]:
                await self._create_story_associations(story_result["story_id"], outline_result["outline"])
            
            if not story_result["success"]:
                return StoryGenerationResponse(
                    success=False,
                    error=story_result["error"],
                    generated_outline=outline_result["outline"],
                    message="Failed to save the generated story to database."
                )
            
            # 5. Return success response
            return StoryGenerationResponse(
                success=True,
                story_id=story_result["story_id"],
                generated_outline=outline_result["outline"],
                summary=self._generate_summary(outline_result["outline"]),
                message="Story generated successfully!"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in story generation: {e}", exc_info=True)
            return StoryGenerationResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                message="An unexpected error occurred. Please try again."
            )
    
    async def _fetch_and_validate_elements(self, world: World, request: StoryGenerationRequest) -> Optional[Dict[str, List[Any]]]:
        """Fetch and validate that all selected elements belong to the world."""
        try:
            elements = {
                "characters": [],
                "locations": [],
                "lore_items": []
            }
            
            # Fetch characters
            if request.selected_characters:
                result = await self.db.execute(
                    select(Character).where(
                        Character.id.in_(request.selected_characters),
                        Character.world_id == world.id
                    )
                )
                elements["characters"] = result.scalars().all()
                if len(elements["characters"]) != len(request.selected_characters):
                    logger.warning(f"Character validation failed: requested {len(request.selected_characters)}, found {len(elements['characters'])}")
                    return None
            
            # Fetch locations
            if request.selected_locations:
                result = await self.db.execute(
                    select(Location).where(
                        Location.id.in_(request.selected_locations),
                        Location.world_id == world.id
                    )
                )
                elements["locations"] = result.scalars().all()
                if len(elements["locations"]) != len(request.selected_locations):
                    logger.warning(f"Location validation failed: requested {len(request.selected_locations)}, found {len(elements['locations'])}")
                    return None
            
            # Fetch lore items
            if request.selected_lore_items:
                result = await self.db.execute(
                    select(LoreItem).where(
                        LoreItem.id.in_(request.selected_lore_items),
                        LoreItem.world_id == world.id
                    )
                )
                elements["lore_items"] = result.scalars().all()
                if len(elements["lore_items"]) != len(request.selected_lore_items):
                    logger.warning(f"Lore item validation failed: requested {len(request.selected_lore_items)}, found {len(elements['lore_items'])}")
                    return None
            
            logger.info(f"Successfully validated {len(elements['characters'])} characters, {len(elements['locations'])} locations, {len(elements['lore_items'])} lore items")
            return elements
            
        except Exception as e:
            logger.error(f"Error fetching/validating elements: {e}", exc_info=True)
            return None
    
    async def _get_ai_model_config(self, config_id: int) -> Optional[AIModelConfiguration]:
        """Get and validate AI model configuration."""
        try:
            # Try cache first
            config = model_cache.get_model_by_id(config_id)
            if config:
                return config
            
            # Fallback to database
            config = await crud_ai_model_config.get_model_config_by_id(self.db, config_id)
            if not config or not config.is_active:
                logger.warning(f"AI model config {config_id} not found or inactive")
                return None
            
            return config
            
        except Exception as e:
            logger.error(f"Error fetching AI model config {config_id}: {e}", exc_info=True)
            return None
    
    async def _generate_story_outline(self, world: World, elements: Dict[str, List[Any]], request: StoryGenerationRequest, ai_model_config: AIModelConfiguration) -> Dict[str, Any]:
        """Generate story outline using AI."""
        try:
            # Import storytelling runtime functions
            from app.services import storytelling_runtime
            
            kernel = storytelling_runtime.kernel
            if not kernel:
                return {"success": False, "error": "Storytelling runtime not available"}
            
            # Prepare input context
            characters_text = self._format_elements_for_ai(elements["characters"], "character")
            locations_text = self._format_elements_for_ai(elements["locations"], "location")
            lore_items_text = self._format_elements_for_ai(elements["lore_items"], "lore_item")
            
            # Get the story generation function using the exported reference
            generate_function = storytelling_runtime.generate_story_structure_function
            if not generate_function:
                logger.error("GenerateStoryStructure function not available in exported functions")
                
                # Check available exported functions
                available_functions = []
                for name, func in [
                    ('review_act_content_function', storytelling_runtime.review_act_content_function),
                    ('generate_act_narrative_only_function', storytelling_runtime.generate_act_narrative_only_function),
                    ('generate_story_structure_function', storytelling_runtime.generate_story_structure_function),
                    ('extract_scenes_from_act_function', storytelling_runtime.extract_scenes_from_act_function)
                ]:
                    if func is not None:
                        available_functions.append(name)
                logger.error(f"Available exported functions: {available_functions}")
                
                # Try direct plugin access as fallback
                try:
                    from app.services.sk_constants import STORY_STRUCTURE_PLUGIN_NAME
                    logger.error(f"Available plugins in kernel: {list(kernel.plugins.keys())}")
                    if STORY_STRUCTURE_PLUGIN_NAME in kernel.plugins:
                        plugin = kernel.plugins[STORY_STRUCTURE_PLUGIN_NAME]
                        # Get function names using proper SK method
                        try:
                            functions_metadata = plugin.get_functions_metadata()
                            function_names = [func.name for func in functions_metadata]
                            logger.error(f"Functions in {STORY_STRUCTURE_PLUGIN_NAME}: {function_names}")
                            
                            # Try to get GenerateStoryStructure using SK plugin access
                            if "GenerateStoryStructure" in function_names:
                                logger.error("GenerateStoryStructure found in plugin functions, using plugin access")
                                generate_function = plugin["GenerateStoryStructure"]
                            else:
                                logger.error("GenerateStoryStructure NOT found in plugin functions")
                        except Exception as plugin_error:
                            logger.error(f"Error accessing plugin functions: {plugin_error}", exc_info=True)
                except Exception as e:
                    logger.error(f"Error checking kernel plugins: {e}", exc_info=True)
                
                # If we still don't have the function after all attempts, return error
                if not generate_function:
                    return {"success": False, "error": "Story generation function not available"}
            
            # Track cost and invoke AI
            start_time = int(time.time() * 1000)
            
            # Log the input parameters for debugging
            logger.info(f"Invoking GenerateStoryStructure with parameters:")
            logger.info(f"  characters: {characters_text[:200]}...")
            logger.info(f"  locations: {locations_text[:200]}...")
            logger.info(f"  lore_items: {lore_items_text[:200]}...")
            logger.info(f"  author_concept: {request.author_concept or 'None'}")
            logger.info(f"  story_genre: {request.story_genre}")
            logger.info(f"  story_tone: {request.story_tone}")
            logger.info(f"  primary_conflict_type: {request.primary_conflict_type}")
            
            # Use direct AI client call instead of storytelling runtime for dynamic model support
            logger.info("Starting AI function invocation with dynamic model...")
            try:
                response_text = await self._call_ai_directly(
                    ai_model_config,
                    world.name,
                    world.description or "No world description provided",
                    characters_text,
                    locations_text,
                    lore_items_text,
                    request.author_concept or "",
                    request.story_genre,
                    request.story_tone,
                    request.primary_conflict_type
                )
                logger.info(f"AI function invocation completed. Response length: {len(response_text) if response_text else 0}")
            except Exception as invoke_error:
                logger.error(f"Error during AI function invocation: {invoke_error}", exc_info=True)
                return {"success": False, "error": f"AI invocation failed: {str(invoke_error)}"}
            
            end_time = int(time.time() * 1000)
            duration_ms = end_time - start_time
            logger.info(f"AI call completed in {duration_ms}ms")
            
            # Check if we got any response at all
            if not response_text or response_text.strip() == "" or response_text.strip() == "None":
                logger.error("No response received from AI model")
                return {
                    "success": False, 
                    "error": "No response received from AI model",
                    "partial_data": {
                        "raw_response": response_text or 'No response',
                        "model_config": f"{ai_model_config.display_name} ({ai_model_config.model_name})"
                    }
                }
            
            logger.info(f"AI response (first 500 chars): {response_text[:500]}")
            
            # Parse JSON response
            outline = await self._parse_ai_response(response_text)
            if not outline:
                return {
                    "success": False, 
                    "error": "Failed to parse AI response as valid JSON",
                    "partial_data": {
                        "raw_response": response_text[:1000],  # Show more of the response
                        "full_response": response_text  # Include full response for debugging
                    }
                }
            
            # Log cost (estimate for now - proper tracking would need token counts)
            input_text = characters_text + locations_text + lore_items_text + (request.author_concept or "") + request.story_genre + request.story_tone + request.primary_conflict_type
            await self.cost_tracker.log_ai_call(
                user_id=self.user.id,
                model_config=ai_model_config,
                input_tokens=len(input_text) // 4,  # Rough estimate
                output_tokens=len(response_text) // 4,  # Rough estimate
                operation_type="story_generation",
                duration_ms=duration_ms,
                object_id=None
            )
            
            return {"success": True, "outline": outline}
            
        except Exception as e:
            logger.error(f"Error generating story outline: {e}", exc_info=True)
            return {"success": False, "error": f"AI generation error: {str(e)}"}
    
    def _format_elements_for_ai(self, elements: List[Any], element_type: str) -> str:
        """Format world elements for AI consumption."""
        if not elements:
            return f"No {element_type}s selected."
        
        formatted = []
        for element in elements:
            if element_type == "character":
                formatted.append(f"- **{element.name}**: {element.description or 'No description'}")
            elif element_type == "location":
                formatted.append(f"- **{element.name}**: {element.description or 'No description'}")
            elif element_type == "lore_item":
                formatted.append(f"- **{element.title}**: {element.description or 'No description'}")
        
        return "\n".join(formatted)
    
    async def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response, handling malformed JSON."""
        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            return self._extract_json_from_text(response_text)
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from potentially malformed text response."""
        try:
            # Look for JSON block between ```json and ```
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Look for JSON object starting with { and ending with }
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            logger.warning("No valid JSON found in AI response")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting JSON from text: {e}")
            return None
    
    async def _create_story_structure(self, world: World, outline: Dict[str, Any], request: StoryGenerationRequest) -> Dict[str, Any]:
        """Create the complete story structure in the database."""
        try:
            # Create the story
            story_data = {
                "title": outline.get("title", "Generated Story"),
                "world_id": world.id,
                "user_id": self.user.id,
                "story_genre": request.story_genre,
                "story_tone": request.story_tone,
                "primary_conflict_type": request.primary_conflict_type,
                "synopsis": self._generate_synopsis(outline)
            }
            
            # Convert dict to schema object
            from app.schemas.story import StoryCreate
            story_create = StoryCreate(**story_data)
            story = await crud_story.create_story(self.db, story_create, self.user.id)
            logger.info(f"Created story '{story.title}' with ID {story.id}")
            
            # Create acts and scenes
            acts_data = outline.get("acts", [])
            for act_index, act_data in enumerate(acts_data, 1):
                act = await self._create_act(story.id, act_index, act_data)
                await self._create_scenes(act.id, act_data.get("scenes", []))
            
            await self.db.commit()
            
            return {"success": True, "story_id": story.id}
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating story structure: {e}", exc_info=True)
            return {"success": False, "error": f"Database error: {str(e)}"}
    
    async def _create_act(self, story_id: int, act_number: int, act_data: Dict[str, Any]) -> Act:
        """Create a single act."""
        act_create_data = {
            "title": act_data.get("name", f"Act {act_number}"),
            "act_number": act_number,
            "description": f"Generated act for {act_data.get('name', f'Act {act_number}')}"
        }
        
        # Convert dict to schema object
        from app.schemas.act import ActCreate
        act_create = ActCreate(**act_create_data)
        act = await crud_act.create_act(self.db, act_create, story_id)
        
        # Flush to get the act ID
        await self.db.flush()
        await self.db.refresh(act)
        
        logger.info(f"Created act '{act.title}' with ID {act.id}")
        
        # Create act-level associations
        await self._create_act_associations(act.id, act_data)
        
        return act
    
    async def _create_scenes(self, act_id: int, scenes_data: List[Dict[str, Any]]) -> None:
        """Create scenes for an act."""
        for scene_data in scenes_data:
            # Extract elements present in the scene
            characters_in_scene = scene_data.get("characters_in_scene", [])
            locations_in_scene = scene_data.get("locations_in_scene", [])
            lore_items_in_scene = scene_data.get("lore_items_in_scene", [])
            
            characters_present = ", ".join(characters_in_scene) if characters_in_scene else None
            
            # Store all scene elements in plot_points as JSON for now
            scene_elements = {
                "characters": characters_in_scene,
                "locations": locations_in_scene,
                "lore_items": lore_items_in_scene
            }
            
            scene_create_data = {
                "title": scene_data.get("title", f"Scene {scene_data.get('number', 1)}"),
                "scene_number": scene_data.get("number", 1),
                "description": scene_data.get("description", "Generated scene"),
                "summary": scene_data.get("description", "Generated scene"),
                "characters_present": characters_present,
                "plot_points": json.dumps(scene_elements)  # Store all elements as JSON
            }
            
            # Convert dict to schema object
            from app.schemas.scene import SceneCreate
            scene_create = SceneCreate(**scene_create_data)
            scene = await crud_scene.create_scene(self.db, scene_create, act_id)
            logger.info(f"Created scene '{scene.title}' with ID {scene.id}")
            
            # Create scene-level associations
            await self._create_scene_associations(scene.id, scene_data)
    
    def _generate_synopsis(self, outline: Dict[str, Any]) -> str:
        """Generate a synopsis from the story outline."""
        title = outline.get("title", "Generated Story")
        genre = outline.get("story_genre", "")
        tone = outline.get("story_tone", "")
        
        synopsis_parts = [f"'{title}' is a {genre.lower()} story" if genre else f"'{title}' is a story"]
        
        if tone:
            synopsis_parts.append(f"with a {tone.lower()} tone")
        
        # Add brief description of the three acts
        acts = outline.get("acts", [])
        if len(acts) >= 3:
            synopsis_parts.append("following a three-act structure")
            
            # Get first scene from each act as a brief summary
            act_summaries = []
            for i, act in enumerate(acts[:3], 1):
                scenes = act.get("scenes", [])
                if scenes:
                    first_scene = scenes[0]
                    act_summaries.append(f"Act {i}: {first_scene.get('description', 'Story development')}")
            
            if act_summaries:
                synopsis_parts.append(". ".join(act_summaries))
        
        return ". ".join(synopsis_parts) + "."
    
    def _generate_summary(self, outline: Dict[str, Any]) -> str:
        """Generate a summary of the generated story."""
        title = outline.get("title", "Generated Story")
        acts = outline.get("acts", [])
        total_scenes = sum(len(act.get("scenes", [])) for act in acts)
        
        return f"Generated '{title}' with {len(acts)} acts and {total_scenes} scenes."
    
    async def _create_act_associations(self, act_id: int, act_data: Dict[str, Any]) -> None:
        """Create associations between an act and its characters, locations, and lore items."""
        from app.models.act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation
        
        # Extract element names from the act data
        characters_in_act = act_data.get("characters_in_act", [])
        locations_in_act = act_data.get("locations_in_act", [])
        lore_items_in_act = act_data.get("lore_items_in_act", [])
        
        # We need to map names back to IDs
        # Get the original elements that were passed to the AI
        if hasattr(self, '_elements_map'):
            elements_map = self._elements_map
        else:
            # If we don't have the map, we'll need to query the database
            # This is a fallback - ideally we should store the elements map
            return
        
        # Create character associations
        for char_name in characters_in_act:
            char = next((c for c in elements_map["characters"] if c.name == char_name), None)
            if char:
                association = ActCharacterAssociation(
                    act_id=act_id,
                    character_id=char.id,
                    roles=["present"]  # Default role
                )
                self.db.add(association)
                logger.info(f"Created act-character association: Act {act_id} - Character {char.id} ({char_name})")
        
        # Create location associations
        for loc_name in locations_in_act:
            loc = next((l for l in elements_map["locations"] if l.name == loc_name), None)
            if loc:
                association = ActLocationAssociation(
                    act_id=act_id,
                    location_id=loc.id,
                    roles=["setting"]  # Default role
                )
                self.db.add(association)
                logger.info(f"Created act-location association: Act {act_id} - Location {loc.id} ({loc_name})")
        
        # Create lore item associations
        for lore_name in lore_items_in_act:
            lore = next((l for l in elements_map["lore_items"] if l.title == lore_name), None)
            if lore:
                association = ActLoreItemAssociation(
                    act_id=act_id,
                    lore_item_id=lore.id,
                    roles=["mentioned"]  # Default role
                )
                self.db.add(association)
                logger.info(f"Created act-lore association: Act {act_id} - Lore {lore.id} ({lore_name})")
    
    async def _create_story_associations(self, story_id: int, outline: Dict[str, Any]) -> None:
        """Create associations between the story and all elements used throughout the story."""
        from app.models.story_associations import StoryCharacterAssociation, StoryLocationAssociation, StoryLoreItemAssociation
        
        # Get all unique elements used across all acts from the outline
        all_characters_used = set(outline.get("all_characters_used", []))
        all_locations_used = set(outline.get("all_locations_used", []))
        all_lore_items_used = set(outline.get("all_lore_items_used", []))
        
        # Get the original elements that were passed to the AI
        if not hasattr(self, '_elements_map'):
            logger.warning("Elements map not available for story-level associations")
            return
        
        elements_map = self._elements_map
        
        # Create story-level character associations
        for char_name in all_characters_used:
            char = next((c for c in elements_map["characters"] if c.name == char_name), None)
            if char:
                association = StoryCharacterAssociation(
                    story_id=story_id,
                    character_id=char.id,
                    roles=["protagonist" if char_name == list(all_characters_used)[0] else "supporting"],  # First character as protagonist
                    notes=f"Featured throughout the story"
                )
                self.db.add(association)
                logger.info(f"Created story-character association: Story {story_id} - Character {char.id} ({char_name})")
        
        # Create story-level location associations
        for loc_name in all_locations_used:
            loc = next((l for l in elements_map["locations"] if l.name == loc_name), None)
            if loc:
                association = StoryLocationAssociation(
                    story_id=story_id,
                    location_id=loc.id,
                    roles=["primary setting" if loc_name == list(all_locations_used)[0] else "setting"],  # First location as primary
                    notes=f"Featured throughout the story"
                )
                self.db.add(association)
                logger.info(f"Created story-location association: Story {story_id} - Location {loc.id} ({loc_name})")
        
        # Create story-level lore item associations
        for lore_name in all_lore_items_used:
            lore = next((l for l in elements_map["lore_items"] if l.title == lore_name), None)
            if lore:
                association = StoryLoreItemAssociation(
                    story_id=story_id,
                    lore_item_id=lore.id,
                    roles=["central element" if lore_name == list(all_lore_items_used)[0] else "referenced"],  # First lore item as central
                    notes=f"Featured throughout the story"
                )
                self.db.add(association)
                logger.info(f"Created story-lore association: Story {story_id} - Lore {lore.id} ({lore_name})")
    
    async def _create_scene_associations(self, scene_id: int, scene_data: Dict[str, Any]) -> None:
        """Create associations between a scene and its characters, locations, and lore items."""
        from app.models.scene_associations import SceneCharacterAssociation, SceneLocationAssociation, SceneLoreItemAssociation
        
        # Extract element names from the scene data
        characters_in_scene = scene_data.get("characters_in_scene", [])
        locations_in_scene = scene_data.get("locations_in_scene", [])
        lore_items_in_scene = scene_data.get("lore_items_in_scene", [])
        
        # Get the original elements that were passed to the AI
        if not hasattr(self, '_elements_map'):
            logger.warning("Elements map not available for scene-level associations")
            return
        
        elements_map = self._elements_map
        
        # Create scene-level character associations
        for char_name in characters_in_scene:
            char = next((c for c in elements_map["characters"] if c.name == char_name), None)
            if char:
                # Determine role based on context
                role = "present"  # Default role
                if len(characters_in_scene) == 1:
                    role = "central focus"
                elif char_name == characters_in_scene[0]:
                    role = "active"
                
                association = SceneCharacterAssociation(
                    scene_id=scene_id,
                    character_id=char.id,
                    roles=[role],
                    notes=f"Appears in scene"
                )
                self.db.add(association)
                logger.info(f"Created scene-character association: Scene {scene_id} - Character {char.id} ({char_name}) with role '{role}'")
        
        # Create scene-level location associations
        for loc_name in locations_in_scene:
            loc = next((l for l in elements_map["locations"] if l.name == loc_name), None)
            if loc:
                # Determine role based on context
                role = "setting"  # Default role
                if loc_name == locations_in_scene[0]:
                    role = "primary location"
                else:
                    role = "secondary location"
                
                association = SceneLocationAssociation(
                    scene_id=scene_id,
                    location_id=loc.id,
                    roles=[role],
                    notes=f"Scene setting"
                )
                self.db.add(association)
                logger.info(f"Created scene-location association: Scene {scene_id} - Location {loc.id} ({loc_name}) with role '{role}'")
        
        # Create scene-level lore item associations
        for lore_name in lore_items_in_scene:
            lore = next((l for l in elements_map["lore_items"] if l.title == lore_name), None)
            if lore:
                # Determine role based on context
                role = "featured"  # Default role
                if len(lore_items_in_scene) == 1:
                    role = "central focus"
                
                association = SceneLoreItemAssociation(
                    scene_id=scene_id,
                    lore_item_id=lore.id,
                    roles=[role],
                    notes=f"Featured in scene"
                )
                self.db.add(association)
                logger.info(f"Created scene-lore association: Scene {scene_id} - Lore {lore.id} ({lore_name}) with role '{role}'")
    
    async def _configure_kernel_for_model(self, kernel, ai_model_config: AIModelConfiguration):
        """Configure the kernel to use the selected AI model. Returns original service for restoration."""
        logger.info(f"Configuring kernel for model: {ai_model_config.display_name} ({ai_model_config.model_name})")
        
        # Store original service for restoration
        chat_service_id = "chat_service"
        original_service = kernel.get_service(chat_service_id)
        
        try:
            if ai_model_config.provider.value in {"OPENROUTER", "OPENAI"}:
                from app.services.langgraph_kernel import OpenAIChatCompletion
                
                new_service = OpenAIChatCompletion(
                    service_id=chat_service_id,
                    ai_model_id=ai_model_config.model_name,
                    api_key=settings.OPENROUTER_API_KEY if ai_model_config.provider.value == "OPENROUTER" else settings.OPENAI_API_KEY,
                    base_url=settings.OPENROUTER_BASE_URL if ai_model_config.provider.value == "OPENROUTER" else None
                )
                kernel.remove_service(chat_service_id)
                kernel.add_service(new_service)
            else:
                logger.warning(f"Unsupported provider: {ai_model_config.provider.value}. Keeping existing kernel service.")
                return original_service
                
            return original_service
            
        except Exception as e:
            logger.error(f"Error configuring kernel for model {ai_model_config.model_name}: {e}", exc_info=True)
            # If configuration fails, ensure we restore the original service
            if original_service:
                try:
                    kernel.remove_service(chat_service_id)
                    kernel.add_service(original_service)
                except:
                    pass
            return None
    
    async def _call_ai_directly(
        self,
        ai_model_config: AIModelConfiguration,
        world_name: str,
        world_description: str,
        characters_text: str,
        locations_text: str,
        lore_items_text: str,
        author_concept: str,
        story_genre: str,
        story_tone: str,
        primary_conflict_type: str
    ) -> str:
        """Call AI directly using AIClientFactory for dynamic model support."""
        try:
            from app.services.ai_client_factory import AIClientFactory
            import time
            
            # Create client based on model provider
            client = AIClientFactory.create_client_for_model(ai_model_config)
            
            # Load the story generation prompt template
            import os
            prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system')
            story_gen_file = os.path.join(prompts_dir, 'story_generation.txt')
            with open(story_gen_file, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            # Replace storytelling runtime variables with actual values
            system_prompt = prompt_template.replace('{{$world_name}}', world_name)
            system_prompt = system_prompt.replace('{{$world_description}}', world_description)
            system_prompt = system_prompt.replace('{{$story_genre}}', story_genre)
            system_prompt = system_prompt.replace('{{$story_tone}}', story_tone)
            system_prompt = system_prompt.replace('{{$primary_conflict_type}}', primary_conflict_type)
            system_prompt = system_prompt.replace('{{$author_concept}}', author_concept)
            system_prompt = system_prompt.replace('{{$characters}}', characters_text)
            system_prompt = system_prompt.replace('{{$locations}}', locations_text)
            system_prompt = system_prompt.replace('{{$lore_items}}', lore_items_text)
            
            # For direct AI calls, we just need the system part without role markers
            # Extract content between <message role="system"> and </message>
            import re
            system_match = re.search(r'<message role="system">(.*?)</message>', system_prompt, re.DOTALL)
            if system_match:
                system_content = system_match.group(1).strip()
            else:
                # Fallback if no role markers found
                system_content = system_prompt
            
            # Extract user message content
            user_match = re.search(r'<message role="user">(.*?)</message>', system_prompt, re.DOTALL)
            if user_match:
                user_message = user_match.group(1).strip()
            else:
                # Fallback user message
                user_message = "Please generate the story outline in the exact JSON format specified above."
            
            # Time the AI call
            start_time = time.perf_counter()
            
            # Use the model configuration from database with provider-aware name resolution
            model_name = AIClientFactory.resolve_model_name(ai_model_config)
            max_tokens = ai_model_config.max_tokens
            temperature = ai_model_config.temperature
            
            logger.info(f"Calling AI with model: {model_name}, max_tokens: {max_tokens}, temperature: {temperature}")
            
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            end_time = time.perf_counter()
            duration_ms = int((end_time - start_time) * 1000)
            
            # Debug the raw response
            logger.debug(f"Raw API response: choices={len(response.choices)}, message={response.choices[0].message}")
            message = response.choices[0].message
            raw_content = message.content
            reasoning_content = getattr(message, 'reasoning_content', None)
            logger.debug(f"Raw content: {repr(raw_content)}")
            logger.debug(f"Reasoning content: {repr(reasoning_content)}")
            
            # DeepSeek and some other models may return response in reasoning_content instead of content
            ai_response = raw_content or reasoning_content or "No response generated."
            logger.info(f"Successfully generated story structure in {duration_ms}ms")
            logger.debug(f"AI response content: {ai_response[:200]}...\" if len(ai_response) > 200 else f\"AI response content: {ai_response}")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error in direct AI call: {e}", exc_info=True)
            raise

    async def _restore_kernel_service(self, kernel, original_service):
        """Restore the original service configuration."""
        # Placeholder for when we implement dynamic service switching
        pass

