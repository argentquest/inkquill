"""Character Generator Service

This service handles the logic for generating characters using AI and random generation.
It integrates with the existing world system and AI infrastructure.
"""

import json
import random
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from app.schemas.character import (
    CharacterGeneratorInput, 
    CharacterGeneratorResult,
    PhysicalAttributes,
    KeyRelationship,
    GenreQuestionAnswer
)
from app.models.character import Character
from app.models.world import World
from app.crud import character as crud_character
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time

# Import cost tracking
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result
from app.services.ai_model_cache import model_cache

logger = logging.getLogger(__name__)

class CharacterGeneratorService:
    """Service for generating characters with AI assistance"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data" / "character_generator"
        self._load_data()
    
    def _load_data(self):
        """Load all the character generation data files"""
        try:
            with open(self.data_path / "personality_traits.json") as f:
                self.personality_traits = json.load(f)
            
            with open(self.data_path / "core_motivations.json") as f:
                self.core_motivations = json.load(f)
            
            with open(self.data_path / "relationship_dynamics.json") as f:
                self.relationship_dynamics = json.load(f)
            
            with open(self.data_path / "physical_attributes.json") as f:
                self.physical_attributes = json.load(f)
            
            with open(self.data_path / "genre_questions.json") as f:
                self.genre_questions = json.load(f)
            
            with open(self.data_path / "professions.json") as f:
                self.professions_data = json.load(f)
                self.professions = self.professions_data["professions"]
            
            with open(self.data_path / "age_categories.json") as f:
                self.age_categories_data = json.load(f)
                self.age_categories = self.age_categories_data["age_categories"]
                
            logger.info("Character generator data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load character generator data: {e}")
            raise
    
    def get_available_genres(self) -> List[str]:
        """Get list of available genres"""
        return list(self.genre_questions.keys())
    
    def get_genre_questions(self, genre: str) -> List[Dict[str, Any]]:
        """Get questions for a specific genre"""
        return self.genre_questions.get(genre, [])
    
    def get_personality_traits(self) -> List[str]:
        """Get available personality traits"""
        return self.personality_traits
    
    def get_core_motivations(self) -> List[str]:
        """Get available core motivations"""
        return self.core_motivations
    
    def get_relationship_dynamics(self) -> List[str]:
        """Get available relationship dynamics"""
        return self.relationship_dynamics
    
    def get_physical_attributes(self) -> Dict[str, List[str]]:
        """Get available physical attributes"""
        return self.physical_attributes
    
    def get_professions(self) -> List[str]:
        """Get available professions"""
        return self.professions
    
    def get_age_categories(self) -> List[str]:
        """Get available age categories"""
        return self.age_categories
    
    def generate_random_character_data(self, world: World) -> CharacterGeneratorInput:
        """Generate completely random character data"""
        
        # Generate random name, gender, and species
        random_name = f"Generated Character {random.randint(1000, 9999)}"
        random_gender = random.choice(["Male", "Female", "Non-binary"])
        
        # Random species with appropriate weighting
        species_choices = [
            "Human", "Human", "Human",  # More likely to be human
            "Elf", "Dwarf", "Halfling", "Orc", "Goblin", 
            "Cat-folk", "Wolf-folk", "Fox-folk",
            "Dragon", "Vampire", "Werewolf", "Angel", "Demon",
            "Wolf", "Cat", "Fox", "Bear"
        ]
        random_species = random.choice(species_choices)
        
        # Random personality traits (4-8 traits)
        num_traits = random.randint(4, 8)
        selected_traits = random.sample(self.personality_traits, num_traits)
        
        # Random core motivations (1-3)
        num_motivations = random.randint(1, 3)
        selected_motivations = random.sample(self.core_motivations, num_motivations)
        
        # Random physical attributes
        physical_attrs = PhysicalAttributes(
            hair_color=random.choice(self.physical_attributes["hair_colors"]),
            eye_color=random.choice(self.physical_attributes["eye_colors"]),
            build=random.choice(self.physical_attributes["builds"]),
            height=random.choice(self.physical_attributes["heights"])
        )
        
        # Random genre and answers
        genre = random.choice(list(self.genre_questions.keys()))
        genre_answers = self._generate_random_genre_answers(genre)
        
        # Random age category and profession
        random_age_category = random.choice(self.age_categories)
        random_profession = random.choice(self.professions)
        
        return CharacterGeneratorInput(
            name=random_name,
            gender=random_gender,
            species=random_species,
            personality_traits=selected_traits,
            core_motivations=selected_motivations,
            physical_attributes=physical_attrs,
            key_relationships=[],  # No relationships
            genre=genre,
            genre_specific_answers=genre_answers,
            age_category=random_age_category,
            profession=random_profession,
            is_random_generation=True
        )
    
    
    def _generate_random_genre_answers(self, genre: str) -> List[GenreQuestionAnswer]:
        """Generate random answers for genre questions"""
        questions = self.genre_questions.get(genre, [])
        answers = []
        
        for question_data in questions:
            question = question_data["question"]
            answer = random.choice(question_data["options"])
            answers.append(GenreQuestionAnswer(question=question, answer=answer))
        
        return answers
    
    async def generate_ai_content(
        self, 
        character_data: CharacterGeneratorInput,
        world: World,
        user_id: int,
        db: AsyncSession
    ) -> Dict[str, str]:
        """Generate AI content including narrative, quest scenario, and first meeting message"""
        
        try:
            # Import storytelling runtime function and kernel instance
            from app.services.storytelling_runtime import kernel, generate_character_backstory_function
            
            # Prepare base character context
            character_context = self._build_character_context(character_data, world)
            
            # Generate different AI content types
            content = {}
            
            # 1. Generate backstory/narrative
            try:
                if generate_character_backstory_function:
                    from app.services.langgraph_kernel import KernelArguments
                    kernel_args = KernelArguments(**character_context)
                    
                    # Track timing for cost logging
                    start_time = time.time()
                    result = await kernel.invoke(generate_character_backstory_function, kernel_args)
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    if result and result.value:
                        # Extract clean text content and filter results
                        narrative_data = self._parse_sk_result(result)
                        content["narrative"] = narrative_data["text"]
                        content["narrative_filter_results"] = narrative_data["filter_results"]
                        
                        # Log AI cost for character generation
                        try:
                            model_config = model_cache.default_generation_model
                            if model_config:
                                # Extract usage data from storytelling runtime result
                                usage_data = get_usage_from_sk_result(result)
                                
                                # Build full prompt for logging
                                input_prompt = self._build_character_prompt_for_logging(character_context)
                                
                                # If no usage data from SK, estimate using tiktoken
                                if not usage_data:
                                    from app.services.cost_tracker_service import estimate_tokens_for_streaming_call
                                    output_text = narrative_data.get("text", "")
                                    usage_data = estimate_tokens_for_streaming_call(
                                        input_text=input_prompt,
                                        output_text=output_text,
                                        model_name=model_config.model_name
                                    )
                                    logger.info(f"Estimated token usage for character generation: {usage_data}")
                                
                                await log_ai_call(
                                    user_id=user_id,
                                    model_config=model_config,
                                    usage=usage_data,
                                    call_type="character_generation",
                                    input_prompt=input_prompt,
                                    duration_ms=duration_ms,
                                    object_id=None,  # No specific object ID for character generation
                                    db=db
                                )
                                logger.info(f"Logged AI cost for character generation: {character_data.name}")
                            else:
                                logger.warning("No default generation model found for character generation cost logging")
                        except Exception as cost_error:
                            logger.error(f"Failed to log AI cost for character generation: {cost_error}")
                            # Don't fail the generation if cost logging fails
                    else:
                        content["narrative"] = "Unable to generate detailed backstory at this time."
                        content["narrative_filter_results"] = None
                else:
                    content["narrative"] = "AI narrative generation not available at this time."
            except Exception as e:
                logger.warning(f"Failed to generate narrative: {e}")
                content["narrative"] = "Unable to generate AI narrative at this time."
            
            # 2. Generate next quest scenario
            try:
                quest_prompt = self._build_quest_scenario_prompt(character_data, world)
                content["next_quest_scenario"] = quest_prompt
            except Exception as e:
                logger.warning(f"Failed to generate quest scenario: {e}")
                content["next_quest_scenario"] = f"Given {character_data.name}'s background and motivations, they would likely seek out adventures that challenge their skills and help them grow."
            
            # 3. Generate first meeting message
            try:
                meeting_message = self._build_first_meeting_message(character_data)
                content["first_meeting_message"] = meeting_message
            except Exception as e:
                logger.warning(f"Failed to generate first meeting message: {e}")
                content["first_meeting_message"] = f"\"Greetings, I am {character_data.name}. It's a pleasure to meet you.\""
            
            # 4. Generate short backstory (50 words max)
            try:
                short_backstory = self._build_short_backstory(character_data, world)
                content["short_backstory"] = short_backstory
            except Exception as e:
                logger.warning(f"Failed to generate short backstory: {e}")
                content["short_backstory"] = f"{character_data.name} is a {character_data.age_category or 'adult'} {character_data.profession or 'adventurer'} with unique traits and motivations."
            
            # 5. Generate visual description prompt
            try:
                visual_prompt = self._build_visual_prompt(character_data)
                content["visual_prompt"] = visual_prompt
            except Exception as e:
                logger.warning(f"Failed to generate visual prompt: {e}")
                content["visual_prompt"] = f"Portrait of {character_data.name}, detailed character art"
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate AI content: {e}")
            return {
                "narrative": "Unable to generate AI narrative at this time.",
                "next_quest_scenario": "Character's next quest is yet to be determined.",
                "first_meeting_message": f"\"Hello, I am {character_data.name or 'a traveler'}.\"",
                "short_backstory": f"{character_data.name or 'This character'} is ready for adventure.",
                "visual_prompt": f"Portrait of {character_data.name or 'a character'}, detailed character art"
            }
    
    def _build_character_context(self, character_data: CharacterGeneratorInput, world: World) -> Dict[str, str]:
        """Build character context for AI generation"""
        variables = {
            "world_name": world.name,
            "world_description": world.description or "A unique fictional world",
            "character_name": character_data.name,
            "personality_traits": ", ".join(character_data.personality_traits) if character_data.personality_traits else "Undefined",
            "core_motivation": ", ".join(character_data.core_motivations) if character_data.core_motivations else "To find their purpose",
            "genre": character_data.genre or "General Fiction",
            "age_category": character_data.age_category or "Adult",
            "profession": character_data.profession or "Adventurer"
        }
        
        # Add gender and species context if provided
        name_context = character_data.name
        if character_data.gender or character_data.species:
            details = []
            if character_data.gender:
                details.append(character_data.gender)
            if character_data.species:
                details.append(character_data.species)
            name_context = f"{character_data.name} ({', '.join(details)})"
        variables["character_name"] = name_context
        
        # No relationships - set to generic
        variables["key_relationships"] = "To be developed through story"
        
        # Format genre answers
        if character_data.genre_specific_answers:
            genre_answers = []
            for qa in character_data.genre_specific_answers:
                genre_answers.append(f"Q: {qa.question} A: {qa.answer}")
            variables["genre_answers"] = "; ".join(genre_answers)
        else:
            variables["genre_answers"] = "None specified"
        
        # Format physical attributes
        if character_data.physical_attributes:
            attrs = character_data.physical_attributes
            phys_parts = []
            if attrs.hair_color:
                phys_parts.append(f"Hair: {attrs.hair_color}")
            if attrs.eye_color:
                phys_parts.append(f"Eyes: {attrs.eye_color}")
            if attrs.build:
                phys_parts.append(f"Build: {attrs.build}")
            if attrs.height:
                phys_parts.append(f"Height: {attrs.height}")
            
            if phys_parts:
                variables["physical_attributes"] = "Physical Attributes: " + ", ".join(phys_parts)
            else:
                variables["physical_attributes"] = ""
        else:
            variables["physical_attributes"] = ""
        
        return variables
    
    def _build_quest_scenario_prompt(self, character_data: CharacterGeneratorInput, world: World) -> str:
        """Generate a quest scenario based on character attributes"""
        name = character_data.name or "the character"
        profession = character_data.profession or "adventurer"
        motivations = character_data.core_motivations or ["seek adventure"]
        personality = character_data.personality_traits or ["determined"]
        
        # Pick primary motivation for quest focus
        main_motivation = motivations[0] if motivations else "seek adventure"
        
        # Build quest scenario based on profession and motivation
        if "treasure" in main_motivation.lower() or "wealth" in main_motivation.lower():
            return f"Having heard rumors of an ancient treasure hidden within the {world.name}, {name} would likely plan to gather information from local taverns and libraries, then assemble a small expedition to explore the most promising leads."
        elif "justice" in main_motivation.lower() or "help" in main_motivation.lower():
            return f"Upon learning of injustices or troubles plaguing the people of {world.name}, {name} would seek out those in need and offer their services as a {profession.lower()}, working to right wrongs and protect the innocent."
        elif "knowledge" in main_motivation.lower() or "wisdom" in main_motivation.lower():
            return f"Driven by their thirst for knowledge, {name} would likely plan to seek out the oldest libraries, wisest scholars, or most mysterious ruins in {world.name} to uncover ancient secrets and expand their understanding."
        elif "power" in main_motivation.lower():
            return f"Ambitious and determined, {name} would likely plan to seek out opportunities to increase their influence, whether through political alliances, magical artifacts, or proving their worth in challenges within {world.name}."
        else:
            return f"As a {profession.lower()} with {', '.join(personality[:2])}, {name} would likely plan their next adventure based on where their skills are most needed in {world.name}, ready to face whatever challenges await."
    
    def _build_first_meeting_message(self, character_data: CharacterGeneratorInput) -> str:
        """Generate a first meeting message based on character personality"""
        name = character_data.name or "a traveler"
        personality = character_data.personality_traits or []
        profession = character_data.profession or "adventurer"
        
        # Choose greeting style based on personality traits
        if any(trait.lower() in ["shy", "introverted", "reserved"] for trait in personality):
            return f"\"Oh, hello there... I'm {name}. I hope I'm not intruding.\""
        elif any(trait.lower() in ["friendly", "outgoing", "cheerful", "enthusiastic"] for trait in personality):
            return f"\"Well hello there, friend! The name's {name}, and it's absolutely wonderful to meet you! What brings you to these parts?\""
        elif any(trait.lower() in ["mysterious", "secretive", "cautious"] for trait in personality):
            return f"\"Greetings, stranger. I am... {name}. What business do you have in these lands?\""
        elif any(trait.lower() in ["arrogant", "proud", "confident"] for trait in personality):
            return f"\"I am {name}, a skilled {profession.lower()}. You should consider yourself fortunate to make my acquaintance.\""
        elif any(trait.lower() in ["wise", "thoughtful", "philosophical"] for trait in personality):
            return f"\"Greetings, fellow traveler. I am {name}. In this vast world, every meeting has its purpose, don't you think?\""
        elif any(trait.lower() in ["aggressive", "fierce", "intimidating"] for trait in personality):
            return f"\"Name's {name}. State your business quickly - I haven't got all day.\""
        else:
            return f"\"Hello there! I'm {name}, a {profession.lower()}. Pleased to make your acquaintance.\""
    
    async def create_character_from_input(
        self,
        db: AsyncSession,
        world_id: int,
        character_input: CharacterGeneratorInput,
        user_id: int,
        background_tasks
    ) -> Character:
        """Create a character in the database from generator input"""
        
        # Get the world for context
        from app.crud import world as crud_world
        world = await crud_world.get_world(db, world_id)
        if not world:
            raise ValueError(f"World {world_id} not found")
        
        # Generate AI content
        ai_content = None
        try:
            ai_content = await self.generate_ai_content(character_input, world, user_id, db)
        except Exception as e:
            logger.warning(f"Failed to generate AI content: {e}")
            ai_content = {
                "narrative": "Unable to generate AI narrative at this time.",
                "next_quest_scenario": "Character's next quest is yet to be determined.",
                "first_meeting_message": f"\"Hello, I am {character_input.name or 'a traveler'}.\"",
                "short_backstory": f"{character_input.name or 'This character'} is ready for adventure.",
                "visual_prompt": f"Portrait of {character_input.name or 'a character'}, detailed character art"
            }
        
        # Prepare character data
        character_data = {
            "name": character_input.name or "Generated Character",
            "gender": character_input.gender,
            "species": character_input.species,
            "description": ai_content.get("short_backstory") if ai_content else "Generated using the Character Generator",
            "personality_traits": ", ".join(character_input.personality_traits) if character_input.personality_traits else None,
            "backstory": ai_content.get("narrative") if ai_content else None,
            "core_motivation": ", ".join(character_input.core_motivations) if character_input.core_motivations else None,  # Legacy field
            "core_motivations": character_input.core_motivations,
            "physical_attributes": character_input.physical_attributes.dict() if character_input.physical_attributes else None,
            "key_relationships": [rel.dict() for rel in character_input.key_relationships] if character_input.key_relationships else None,
            "genre": character_input.genre,
            "genre_specific_answers": {qa.question: qa.answer for qa in character_input.genre_specific_answers} if character_input.genre_specific_answers else None,
            "generated_narrative": ai_content.get("narrative") if ai_content else None,
            "is_ai_generated": True,
            # New fields
            "next_quest_scenario": ai_content.get("next_quest_scenario") if ai_content else None,
            "first_meeting_message": ai_content.get("first_meeting_message") if ai_content else None,
            "age_category": character_input.age_category,
            "profession": character_input.profession,
            "short_backstory": ai_content.get("short_backstory") if ai_content else None,
            "visual_prompt": ai_content.get("visual_prompt") if ai_content else None,
            "narrative_filter_results": ai_content.get("narrative_filter_results") if ai_content else None
        }
        
        # Create character
        from app.schemas.character import CharacterCreate
        character_create = CharacterCreate(**character_data)
        character = await crud_character.create_character(db, character_create, world_id, user_id, background_tasks)
        
        # Generate image if physical attributes are provided
        if character_input.physical_attributes:
            try:
                await self._generate_character_image(character, character_input)
            except Exception as e:
                logger.warning(f"Failed to generate character image: {e}")
        
        return character
    
    async def _generate_character_image(
        self, 
        character: Character, 
        character_input: CharacterGeneratorInput
    ):
        """Generate character image using existing image generation pipeline"""
        
        if not character_input.physical_attributes:
            return
        
        # Build image prompt from physical attributes and personality
        prompt_parts = []
        
        # Physical attributes
        attrs = character_input.physical_attributes
        if attrs.hair_color:
            prompt_parts.append(f"{attrs.hair_color.lower()} hair")
        if attrs.eye_color:
            prompt_parts.append(f"{attrs.eye_color.lower()} eyes")
        if attrs.build:
            prompt_parts.append(f"{attrs.build.lower()} build")
        
        # Add some personality context
        if character_input.personality_traits:
            # Pick 2-3 visual personality traits
            visual_traits = [trait for trait in character_input.personality_traits 
                           if trait.lower() in ['mysterious', 'elegant', 'rugged', 'gentle', 'fierce', 'wise']][:2]
            if visual_traits:
                prompt_parts.append(f"{', '.join(visual_traits).lower()} expression")
        
        # Genre context for styling
        if character_input.genre:
            genre_styles = {
                "Fantasy": "fantasy character, medieval styling",
                "Sci-Fi": "futuristic character, sci-fi styling", 
                "Horror": "dark atmospheric character",
                "Mystery": "detective noir styling",
                "Romance": "elegant romantic styling"
            }
            if character_input.genre in genre_styles:
                prompt_parts.append(genre_styles[character_input.genre])
        
        # Combine into prompt
        image_prompt = f"Portrait of {character.name}, " + ", ".join(prompt_parts) + ", detailed character art, high quality"
        
        # Use existing image generation service
        # This should integrate with your existing image generation pipeline
        try:
            # The actual implementation would depend on your existing image generation setup
            # await image_generation_service.generate_character_image(character, image_prompt)
            logger.info(f"Image prompt generated for {character.name}: {image_prompt}")
        except Exception as e:
            logger.error(f"Failed to generate image for character {character.name}: {e}")
    
    def _build_short_backstory(self, character_data: CharacterGeneratorInput, world: World) -> str:
        """Generate a short backstory (50 words max) based on character attributes"""
        name = character_data.name or "The character"
        profession = character_data.profession or "adventurer"
        age_category = character_data.age_category or "adult"
        species = character_data.species or "individual"
        main_trait = character_data.personality_traits[0] if character_data.personality_traits else "determined"
        main_motivation = character_data.core_motivations[0] if character_data.core_motivations else "seek adventure"
        
        # Build concise backstory
        if "young" in age_category.lower() or age_category.lower() == "child":
            return f"{name} is a {main_trait.lower()} young {species} {profession.lower()} from {world.name}. Despite their youth, they are driven to {main_motivation.lower()}, showing remarkable potential for their age."
        elif "elder" in age_category.lower() or "ancient" in age_category.lower():
            return f"{name} is a wise {age_category.lower()} {species} {profession.lower()} who has spent decades in {world.name}. Their {main_trait.lower()} nature and desire to {main_motivation.lower()} guide their actions."
        else:
            return f"{name} is a {main_trait.lower()} {age_category.lower()} {species} {profession.lower()} from {world.name}. Motivated to {main_motivation.lower()}, they navigate their world with purpose and determination."
    
    def _build_visual_prompt(self, character_data: CharacterGeneratorInput) -> str:
        """Generate a visual description prompt for character image generation"""
        prompt_parts = []
        
        # Basic info
        if character_data.age_category:
            age_descriptors = {
                "Child": "young child",
                "Teenager": "teenage",
                "Young Adult": "young adult", 
                "Adult": "adult",
                "Middle-aged": "middle-aged",
                "Elder": "elderly",
                "Ancient": "ancient, wise"
            }
            prompt_parts.append(age_descriptors.get(character_data.age_category, "adult"))
        
        if character_data.gender:
            prompt_parts.append(character_data.gender.lower())
        
        if character_data.species and character_data.species.lower() != "human":
            prompt_parts.append(character_data.species.lower())
        
        # Profession/occupation styling
        if character_data.profession:
            profession_styles = {
                "Warrior": "armored warrior with weapons",
                "Mage": "robed spellcaster with magical aura",
                "Wizard": "wise wizard with staff and robes",
                "Knight": "noble knight in shining armor",
                "Rogue": "stealthy figure in dark clothing",
                "Assassin": "shadowy figure with hidden weapons",
                "Priest": "holy figure in religious garments",
                "Cleric": "divine healer with holy symbols",
                "Paladin": "righteous warrior in blessed armor",
                "Bard": "charismatic performer with musical instrument",
                "Scholar": "learned individual with books and scrolls",
                "Alchemist": "experimenter with potions and tools",
                "Blacksmith": "strong craftsperson with forge tools",
                "Merchant": "well-dressed trader with goods",
                "Noble": "aristocrat in fine clothing and jewelry"
            }
            style = profession_styles.get(character_data.profession, f"{character_data.profession.lower()} professional attire")
            prompt_parts.append(style)
        
        # Physical attributes
        if character_data.physical_attributes:
            attrs = character_data.physical_attributes
            if attrs.hair_color:
                prompt_parts.append(f"{attrs.hair_color.lower()} hair")
            if attrs.eye_color:
                prompt_parts.append(f"{attrs.eye_color.lower()} eyes")
            if attrs.build:
                build_descriptors = {
                    "Slim": "slender build",
                    "Athletic": "athletic build", 
                    "Muscular": "muscular build",
                    "Heavy": "heavy build",
                    "Average": "average build"
                }
                prompt_parts.append(build_descriptors.get(attrs.build, f"{attrs.build.lower()} build"))
        
        # Personality-based visual cues
        if character_data.personality_traits:
            visual_traits = []
            for trait in character_data.personality_traits[:3]:  # Max 3 traits
                trait_expressions = {
                    "Confident": "confident posture and expression",
                    "Mysterious": "enigmatic smile and shadowed features",
                    "Friendly": "warm smile and open expression",
                    "Fierce": "intense gaze and strong stance",
                    "Wise": "thoughtful expression and knowing eyes",
                    "Cheerful": "bright smile and energetic pose",
                    "Elegant": "graceful posture and refined features",
                    "Rugged": "weathered features and sturdy build"
                }
                if trait in trait_expressions:
                    visual_traits.append(trait_expressions[trait])
            
            if visual_traits:
                prompt_parts.extend(visual_traits[:2])  # Max 2 personality visual cues
        
        # Genre styling
        if character_data.genre:
            genre_styles = {
                "Fantasy": "fantasy art style, magical atmosphere",
                "Sci-Fi": "futuristic setting, sci-fi elements",
                "Horror": "dark atmosphere, dramatic lighting",
                "Mystery": "noir atmosphere, dramatic shadows",
                "Romance": "soft lighting, elegant composition"
            }
            if character_data.genre in genre_styles:
                prompt_parts.append(genre_styles[character_data.genre])
        
        # Combine into final prompt
        base_prompt = f"Portrait of {character_data.name or 'a character'}"
        if prompt_parts:
            full_prompt = f"{base_prompt}, {', '.join(prompt_parts)}, highly detailed character art, professional quality"
        else:
            full_prompt = f"{base_prompt}, detailed character portrait, professional quality"
        
        return full_prompt
    
    def _build_character_prompt_for_logging(self, character_context: Dict[str, str]) -> str:
        """Build a summary prompt string for cost logging purposes"""
        prompt_parts = []
        
        if character_context.get("character_name"):
            prompt_parts.append(f"Character: {character_context['character_name']}")
        if character_context.get("world_name"):
            prompt_parts.append(f"World: {character_context['world_name']}")
        if character_context.get("genre"):
            prompt_parts.append(f"Genre: {character_context['genre']}")
        if character_context.get("profession"):
            prompt_parts.append(f"Profession: {character_context['profession']}")
        if character_context.get("age_category"):
            prompt_parts.append(f"Age: {character_context['age_category']}")
        if character_context.get("personality_traits"):
            prompt_parts.append(f"Traits: {character_context['personality_traits']}")
        if character_context.get("core_motivation"):
            prompt_parts.append(f"Motivation: {character_context['core_motivation']}")
        
        return "Character Generation Request: " + " | ".join(prompt_parts)
    
    def _parse_sk_result(self, result) -> Dict[str, Any]:
        """Parse storytelling runtime result to extract clean text and filter results"""
        try:
            result_str = str(result.value)
            
            # Try to extract just the text content if it's wrapped in JSON-like format
            if "ChatMessageContent" in result_str:
                # Look for the actual text content in the string representation
                import re
                
                # Try multiple extraction patterns
                clean_text = None
                
                # Pattern 1: Look for text='...' (with proper multiline handling)
                text_match = re.search(r"text='([^']*(?:\\.[^']*)*)'", result_str, re.DOTALL)
                if text_match:
                    clean_text = text_match.group(1)
                
                # Pattern 2: Look for the actual story content (multiple paragraphs)
                if not clean_text:
                    # Look for long text content that looks like a story
                    story_pattern = r'In [^,]+, \w+.*?(?=\', |\", |encoding=|finish_reason=|$)'
                    story_match = re.search(story_pattern, result_str, re.DOTALL)
                    if story_match:
                        clean_text = story_match.group(0)
                
                # Pattern 3: Fallback - extract content between specific markers
                if not clean_text:
                    content_match = re.search(r'ChatCompletion.*?content=\'([^\']+)\'', result_str, re.DOTALL)
                    if content_match:
                        clean_text = content_match.group(1)
                
                # Pattern 4: Last resort - just clean up the whole string
                if not clean_text:
                    clean_text = result_str
                
                # Extract prompt_filter_results
                filter_results = None
                if "prompt_filter_results" in result_str:
                    try:
                        import json
                        # Try to extract the filter results JSON - improved pattern
                        filter_patterns = [
                            r"'prompt_filter_results': (\[.*?\])",
                            r'"prompt_filter_results": (\[.*?\])',
                            r'prompt_filter_results=(\[.*?\])',
                        ]
                        
                        for pattern in filter_patterns:
                            filter_match = re.search(pattern, result_str, re.DOTALL)
                            if filter_match:
                                try:
                                    # Try to safely evaluate the extracted JSON
                                    filter_text = filter_match.group(1)
                                    # Replace single quotes with double quotes for valid JSON
                                    filter_text = filter_text.replace("'", '"').replace('False', 'false').replace('True', 'true')
                                    parsed_results = json.loads(filter_text)
                                    
                                    # Extract content_filter_results from the first item if it's a list
                                    if isinstance(parsed_results, list) and len(parsed_results) > 0:
                                        filter_results = parsed_results[0].get('content_filter_results', parsed_results[0])
                                    else:
                                        filter_results = parsed_results
                                    break
                                except:
                                    continue
                    except Exception as e:
                        logger.warning(f"Failed to parse filter results: {e}")
                        filter_results = None
                
                return {
                    "text": clean_text.strip(),
                    "filter_results": filter_results
                }
            else:
                # Simple text result
                return {
                    "text": result_str.strip(),
                    "filter_results": None
                }
                
        except Exception as e:
            logger.error(f"Failed to parse SK result: {e}")
            return {
                "text": str(result.value) if result and result.value else "Error parsing result",
                "filter_results": None
            }

# Global service instance
character_generator_service = CharacterGeneratorService()
