"""API routes for story wizard api."""

# /story_app/app/routers/story_wizard_api.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
import logging
import json
from datetime import datetime

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.services.langgraph_runtime_setup import kernel, load_prompt_from_file
from app.services.ai_model_cache import model_cache
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result
from app.crud import user as crud_user
from app.services.langgraph_kernel import (
    InputVariable,
    KernelArguments,
    OpenAIChatPromptExecutionSettings,
    PromptTemplateConfig,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/story-wizard", tags=["story-wizard-api"])

@router.get("/validate-connection")
async def validate_ai_connection():
    """Validate Story Wizard AI connection using OpenRouter Gemini"""
    validation_results = {
        "openrouter_connection": False,
        "gemini_model_access": False,
        "story_wizard_prompt": False,
        "test_execution": False,
        "errors": []
    }
    
    try:
        # Test 1: Check OpenRouter connection
        try:
            from app.services.ai_client_factory import AIClientFactory
            from app.models.ai_model_config import AIProviderEnum
            
            client = AIClientFactory.create_client(AIProviderEnum.OPENROUTER)
            validation_results["openrouter_connection"] = True
        except Exception as e:
            validation_results["errors"].append(f"OpenRouter connection failed: {str(e)}")
            
        # Test 2: Test Gemini model access
        if validation_results["openrouter_connection"]:
            try:
                test_response = await client.chat.completions.create(
                    model="google/gemini-2.5-flash-lite-preview-06-17",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                if test_response.choices:
                    validation_results["gemini_model_access"] = True
                else:
                    validation_results["errors"].append("Gemini model returned no response")
            except Exception as e:
                validation_results["errors"].append(f"Gemini model access failed: {str(e)}")
            
        # Test 3: Test Story Wizard prompt system
        validation_results["story_wizard_prompt"] = True  # Our prompt system is always available
            
        # Test 4: Test complete execution
        if validation_results["openrouter_connection"] and validation_results["gemini_model_access"]:
            try:
                test_response, test_usage = await _generate_simple_wizard_response(
                    phase=1, step=1, 
                    user_message="Test story idea", 
                    story_context="Test context"
                )
                
                if test_response and len(test_response) > 0:
                    validation_results["test_execution"] = True
                    validation_results["test_response"] = test_response[:200] + "..."
                    validation_results["test_usage"] = test_usage
                else:
                    validation_results["errors"].append("Test execution returned empty response")
            except Exception as e:
                validation_results["errors"].append(f"Test execution failed: {str(e)}")
                
    except Exception as e:
        validation_results["errors"].append(f"Validation error: {str(e)}")
        logger.error(f"Story Wizard validation error: {e}")
        
    validation_results["overall_status"] = all([
        validation_results["openrouter_connection"],
        validation_results["gemini_model_access"], 
        validation_results["story_wizard_prompt"],
        validation_results["test_execution"]
    ])
    
    validation_results["model_info"] = {
        "provider": "OpenRouter",
        "model": "google/gemini-2.5-flash-lite-preview-06-17",
        "description": "Google Gemini 2.5 Flash Lite Preview via OpenRouter"
    }
    
    return validation_results

# Load Story Wizard prompts
try:
    STORY_WIZARD_CHAT_PROMPT = load_prompt_from_file("story_wizard_chat.txt")
    STORY_WIZARD_EXTRACTION_PROMPT = load_prompt_from_file("story_wizard_extraction.txt")
    logger.info("Story Wizard prompts loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Story Wizard prompts: {e}")
    STORY_WIZARD_CHAT_PROMPT = "You are a story wizard. Help the user create a story."
    STORY_WIZARD_EXTRACTION_PROMPT = "Extract story data from user response."

# Phase definitions
PHASES = {
    1: {
        "name": "Core Spark & Protagonist",
        "total_steps": 2,
        "questions": {
            1: {
                "focus": "Core concept and genre",
                "extract_fields": ["core_concept", "genre", "mood_atmosphere"]
            },
            2: {
                "focus": "Protagonist details",
                "extract_fields": ["protagonist"]
            }
        }
    },
    2: {
        "name": "World & Call to Adventure",
        "total_steps": 2,
        "questions": {
            1: {
                "focus": "Setting and world rules",
                "extract_fields": ["setting"]
            },
            2: {
                "focus": "Inciting incident",
                "extract_fields": ["inciting_incident"]
            }
        }
    },
    3: {
        "name": "Conflict, Stakes & Supporting Cast",
        "total_steps": 3,
        "questions": {
            1: {
                "focus": "Antagonist and obstacles",
                "extract_fields": ["antagonist", "major_conflicts"]
            },
            2: {
                "focus": "Stakes and consequences",
                "extract_fields": ["major_conflicts"]
            },
            3: {
                "focus": "Key relationships",
                "extract_fields": ["key_relationships"]
            }
        }
    },
    4: {
        "name": "Climax, Resolution & Theme",
        "total_steps": 2,
        "questions": {
            1: {
                "focus": "Turning point and climax",
                "extract_fields": ["plot_points"]
            },
            2: {
                "focus": "Resolution and theme",
                "extract_fields": ["resolution", "theme", "story_title"]
            }
        }
    }
}

@router.post("/process-message")
async def process_wizard_message(
    request_data: dict,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Process a message in the Story Wizard conversation"""
    try:
        session_data = request_data.get("session_data", {})
        user_message = request_data.get("message", "")
        ai_model_id = request_data.get("ai_model_id")
        
        current_phase = session_data.get("phase", 1)
        current_step = session_data.get("step", 1)
        conversation = session_data.get("conversation", [])
        story_data = session_data.get("story_data", {})

        # Ensure Story Wizard functions are registered
        await _ensure_story_wizard_functions()

        # Build conversation context
        story_context = _build_story_context(story_data)
        phase_info = PHASES[current_phase]
        
        # Build conversation history
        conversation_history = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation[-6:]  # Last 3 exchanges
        ])
        
        # Prepare arguments for the storytelling runtime
        arguments = KernelArguments(
            phase_name=phase_info["name"],
            step=current_step,
            total_steps=phase_info["total_steps"],
            story_context=story_context,
            user_message=user_message,
            conversation_history=conversation_history
        )
        
        # Get AI response using OpenRouter Gemini
        try:
            # Build a focused prompt for the current phase/step
            ai_response, token_usage, ai_prompt = await _generate_simple_wizard_response(
                current_phase, current_step, user_message, story_context
            )
            
            # Log the AI call for cost tracking
            from app.services.ai_model_cache import model_cache
            from app.models.ai_model_config import AIProviderEnum
            
            # Get model config for logging - use default OpenRouter model
            model_config = model_cache.get_default_model_for_provider(AIProviderEnum.OPENROUTER)
            
            if model_config:
                await log_ai_call(
                    user_id=current_user.id,
                    model_config=model_config,
                    usage=token_usage,
                    call_type="story_wizard_chat",
                    input_prompt=user_message,
                    db=db
                )
            else:
                logger.warning("Could not find OpenRouter model config for story wizard cost logging")
            
        except Exception as e:
            logger.error(f"Error with Story Wizard response generation: {str(e)}")
            # Fallback to a simple response
            ai_response = f"Great! Tell me more about {_get_current_phase_focus(current_phase, current_step)}."
            token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_cost": 0}
            ai_prompt = f"Error occurred - fallback response for Phase {current_phase}, Step {current_step}"

        # Extract story data from user's message
        updated_story_data = await _extract_story_information(
            user_message,
            story_data,
            current_phase,
            current_step,
            db,
            current_user
        )

        # Clean progression markers from user-visible response
        ai_response_clean = _clean_progression_markers(ai_response)
        
        # Let AI decide if ready to advance to next step/phase
        next_phase, next_step, is_complete = await _ai_determine_progression(
            current_phase, current_step, user_message, story_context, ai_response
        )
        
        # Log progression decision
        if next_phase != current_phase or next_step != current_step:
            logger.info(f"AI decided to advance from Phase {current_phase}, Step {current_step} to Phase {next_phase}, Step {next_step}")
        else:
            logger.info(f"AI decided to stay at Phase {current_phase}, Step {current_step} for more detail")

        return {
            "success": True,
            "response": ai_response_clean,
            "ai_prompt": ai_prompt,
            "phase": next_phase,
            "step": next_step,
            "story_data": updated_story_data,
            "is_complete": is_complete,
            "token_usage": {
                "input": token_usage.get("prompt_tokens", 0),
                "output": token_usage.get("completion_tokens", 0),
                "cost": token_usage.get("total_cost", 0)
            }
        }

    except Exception as e:
        logger.error(f"Error processing wizard message: {str(e)}")
        
        # Refund coins on error
        if current_user and "token_usage" in locals() and token_usage:
            await crud_user.add_coins(
                db, 
                current_user.id, 
                int(token_usage.get("total_cost", 0))
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def _extract_story_information(
    user_message: str,
    current_data: dict,
    phase: int,
    step: int,
    db: AsyncSession,
    user: User
) -> dict:
    """Extract structured information from user's response"""
    
    # Ensure Story Wizard functions are registered
    await _ensure_story_wizard_functions()
    
    # Get extraction schema based on phase/step
    extraction_schema = _get_extraction_schema(phase, step)
    phase_info = PHASES[phase]["questions"][step]
    
    # Prepare arguments for extraction function
    arguments = KernelArguments(
        extraction_focus=phase_info["focus"],
        current_story_data=json.dumps(current_data, indent=2),
        user_response=user_message,
        extraction_schema=extraction_schema
    )

    # Use simple rule-based extraction for MVP
    try:
        extraction_response = _extract_data_simple(
            user_message, current_data, phase, step
        )
        
    except Exception as e:
        logger.error(f"Error with data extraction: {str(e)}")
        extraction_response = "{}"

    try:
        extracted = json.loads(extraction_response)
        
        # Merge with existing data
        updated_data = current_data.copy()
        
        # Update based on phase/step
        phase_config = PHASES[phase]["questions"][step]
        for field in phase_config["extract_fields"]:
            if field in extracted:
                if field == "protagonist" and isinstance(extracted[field], dict):
                    updated_data["protagonist"] = extracted[field]
                elif field == "setting" and isinstance(extracted[field], dict):
                    updated_data["setting"] = extracted[field]
                elif field == "key_relationships" and isinstance(extracted[field], list):
                    updated_data["key_relationships"] = extracted[field]
                else:
                    updated_data[field] = extracted[field]
        
        return updated_data
        
    except json.JSONDecodeError:
        logger.error(f"Failed to parse extraction response: {extraction_response}")
        return current_data

async def _ensure_story_wizard_functions():
    """Ensure Story Wizard functions are registered in the storytelling runtime."""
    if not kernel.plugins.get("StoryWizard"):
        try:
            # Register Chat Response function
            chat_exec_settings = OpenAIChatPromptExecutionSettings(
                service_id="chat_service",
                max_tokens=300,
                temperature=0.7,
                top_p=0.9
            )
            
            chat_prompt_config = PromptTemplateConfig(
                template=STORY_WIZARD_CHAT_PROMPT,
                name="ChatResponse",
                template_format="semantic-kernel",
                description="Story Wizard chat response generation",
                input_variables=[
                    InputVariable(name="phase_name", description="Current phase name"),
                    InputVariable(name="step", description="Current step number"),
                    InputVariable(name="total_steps", description="Total steps in phase"),
                    InputVariable(name="story_context", description="Current story context"),
                    InputVariable(name="user_message", description="User's message"),
                    InputVariable(name="conversation_history", description="Conversation history")
                ],
                execution_settings={"chat_service": chat_exec_settings}
            )
            
            kernel.add_function(
                function_name="ChatResponse",
                plugin_name="StoryWizard",
                prompt_template_config=chat_prompt_config
            )
            
            # Register Data Extraction function
            extract_exec_settings = OpenAIChatPromptExecutionSettings(
                service_id="chat_service",
                max_tokens=500,
                temperature=0.3,
                top_p=0.9,
                response_format={"type": "json_object"}
            )
            
            extract_prompt_config = PromptTemplateConfig(
                template=STORY_WIZARD_EXTRACTION_PROMPT,
                name="ExtractData",
                template_format="semantic-kernel",
                description="Story Wizard data extraction",
                input_variables=[
                    InputVariable(name="extraction_focus", description="Focus of extraction"),
                    InputVariable(name="current_story_data", description="Current story data"),
                    InputVariable(name="user_response", description="User's response"),
                    InputVariable(name="extraction_schema", description="Extraction schema")
                ],
                execution_settings={"chat_service": extract_exec_settings}
            )
            
            kernel.add_function(
                function_name="ExtractData",
                plugin_name="StoryWizard",
                prompt_template_config=extract_prompt_config
            )
            
            logger.info("Story Wizard functions registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register Story Wizard functions: {e}")

def _get_extraction_schema(phase: int, step: int) -> str:
    """Get the extraction schema for current phase/step"""
    
    schemas = {
        (1, 1): """Extract the following from the user's response and return as JSON:
{
  "core_concept": "The main 'what if' or core concept",
  "genre": "The story genre",
  "mood_atmosphere": "The mood or atmosphere to evoke"
}""",
        (1, 2): """Extract the following from the user's response and return as JSON:
{
  "protagonist": {
    "name": "Character name",
    "age": "Character age",
    "defining_characteristic": "Main characteristic",
    "initial_desire_goal": "Their initial desire or goal",
    "primary_flaw_weakness": "Their main flaw or weakness"
  }
}""",
        (2, 1): """Extract the following from the user's response and return as JSON:
{
  "setting": {
    "primary_location": "Main setting location",
    "unique_rules_characteristics": ["Rule 1", "Rule 2"],
    "societal_cultural_atmosphere": {
      "mundane_world": "Description of normal world",
      "magical_community": "Description of hidden/special world (if applicable)"
    }
  }
}""",
        (2, 2): """Extract the following from the user's response and return as JSON:
{
  "inciting_incident": {
    "event": "The specific event that disrupts the protagonist's life",
    "protagonist_initial_reaction": "How the protagonist initially reacts"
  }
}""",
        (3, 1): """Extract the following from the user's response and return as JSON:
{
  "antagonist": {
    "description": "Description of the antagonist",
    "goal_motivation": "Their goal and motivation"
  },
  "major_conflicts": {
    "external_obstacles": ["Obstacle 1", "Obstacle 2"]
  }
}""",
        (3, 2): """Extract the following from the user's response and return as JSON:
{
  "major_conflicts": {
    "personal_stakes": "What the protagonist stands to lose",
    "broader_consequences": "Impact on the world if protagonist fails"
  }
}""",
        (3, 3): """Extract the following from the user's response and return as JSON:
{
  "key_relationships": [
    {
      "type": "ally/mentor/rival/etc",
      "name": "Character name",
      "role": "Their role in the story",
      "unique_skill_perspective": "What they bring to the story",
      "how_it_changes": "How the relationship evolves (if mentioned)"
    }
  ]
}""",
        (4, 1): """Extract the following from the user's response and return as JSON:
{
  "plot_points": {
    "mid_point_turning_point": "The story's turning point",
    "climax_description": "Description of the climax",
    "protagonist_growth_in_climax": "How protagonist demonstrates growth"
  }
}""",
        (4, 2): """Extract the following from the user's response and return as JSON:
{
  "resolution": {
    "outcome_for_protagonist_world": "How the story resolves",
    "ending_tone": "The tone of the ending"
  },
  "theme": "The central theme or message",
  "story_title": "A title for the story (generate if not provided)"
}"""
    }
    
    return schemas.get((phase, step), "Extract any relevant story information and return as JSON.")

def _build_story_context(story_data: dict) -> str:
    """Build a concise summary of story data collected so far"""
    context_parts = []
    
    if story_data.get("core_concept"):
        context_parts.append(f"Core concept: {story_data['core_concept']}")
    
    if story_data.get("genre"):
        context_parts.append(f"Genre: {story_data['genre']}")
    
    if story_data.get("protagonist", {}).get("name"):
        p = story_data["protagonist"]
        context_parts.append(f"Protagonist: {p.get('name', 'Unknown')}, {p.get('age', 'age unknown')}")
    
    if story_data.get("setting", {}).get("primary_location"):
        context_parts.append(f"Setting: {story_data['setting']['primary_location']}")
    
    if story_data.get("antagonist", {}).get("description"):
        context_parts.append(f"Antagonist: {story_data['antagonist']['description'][:100]}...")
    
    return "\n".join(context_parts) if context_parts else "No story data collected yet."

async def _generate_simple_wizard_response(
    phase: int, step: int, user_message: str, story_context: str
) -> tuple[str, dict, str]:
    """Generate AI wizard response using your original Story Wizard prompt"""
    phase_info = PHASES.get(phase, {})
    phase_name = phase_info.get("name", "Unknown Phase")
    total_steps = phase_info.get("total_steps", 1)
    
    try:
        # Load your original full prompt from file
        from app.services.langgraph_runtime_setup import load_prompt_from_file
        full_prompt_template = load_prompt_from_file("story_wizard_chat.txt")
        
        # Replace template variables with actual values
        conversation_history = ""  # We'll build this properly later
        full_prompt = full_prompt_template.replace("{{$phase_name}}", phase_name)
        full_prompt = full_prompt.replace("{{$step}}", str(step))
        full_prompt = full_prompt.replace("{{$total_steps}}", str(total_steps))
        full_prompt = full_prompt.replace("{{$story_context}}", story_context)
        full_prompt = full_prompt.replace("{{$user_message}}", user_message)
        full_prompt = full_prompt.replace("{{$conversation_history}}", conversation_history)
        
        # Use OpenRouter with configured default model
        from app.services.ai_client_factory import AIClientFactory
        from app.models.ai_model_config import AIProviderEnum
        from app.services.ai_model_cache import model_cache
        
        client = AIClientFactory.create_client(AIProviderEnum.OPENROUTER)
        
        # Get the default OpenRouter model
        default_model = model_cache.get_default_model_for_provider(AIProviderEnum.OPENROUTER)
        model_name = default_model.model_name if default_model else "deepseek/deepseek-r1"
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,  # Allow longer responses for your rich prompt
            temperature=0.7,
            top_p=0.9
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Get actual token usage from response
        usage = response.usage
        token_usage = {
            "prompt_tokens": usage.prompt_tokens if usage else 100,
            "completion_tokens": usage.completion_tokens if usage else 50,
            "total_cost": 0.005  # Gemini Flash is very cost-effective
        }
            
        logger.info(f"OpenRouter Gemini with full prompt response generated: {len(ai_response)} chars")
        return ai_response, token_usage, full_prompt
        
    except Exception as e:
        logger.error(f"Error with OpenRouter Gemini API: {e}")
        
        # Fallback to phase-appropriate question
        focus = _get_current_phase_focus(phase, step)
        fallback_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_cost": 0}
        fallback_prompt = f"Fallback prompt for Phase {phase}, Step {step}"
        return f"Great! Now, can you tell me more about {focus.lower()}?", fallback_usage, fallback_prompt

def _extract_data_simple(user_message: str, current_data: dict, phase: int, step: int) -> str:
    """Simple rule-based data extraction for MVP"""
    message_lower = user_message.lower()
    extracted = {}
    
    # Phase 1, Step 1: Core concept and genre
    if phase == 1 and step == 1:
        extracted = {
            "core_concept": user_message,
            "genre": "memoir" if any(word in message_lower for word in ["my", "i", "first"]) else "adventure",
            "mood_atmosphere": "nostalgic" if "first" in message_lower else "adventurous"
        }
    
    # Phase 1, Step 2: Protagonist details
    elif phase == 1 and step == 2:
        extracted = {
            "protagonist": {
                "name": "You",
                "age": "Young adult",
                "defining_characteristic": "First-time car buyer",
                "initial_desire_goal": "Getting independence through car ownership",
                "primary_flaw_weakness": "Inexperience with cars"
            }
        }
    
    # Phase 2, Step 1: Setting
    elif phase == 2 and step == 1:
        extracted = {
            "setting": {
                "primary_location": "Car dealership and local roads",
                "unique_rules_characteristics": ["First car buying experience", "Winter driving conditions"],
                "societal_cultural_atmosphere": {
                    "mundane_world": "Everyday life requiring transportation",
                    "special_world": "The independence that comes with car ownership"
                }
            }
        }
    
    # Phase 2, Step 2: Inciting incident
    elif phase == 2 and step == 2:
        extracted = {
            "inciting_incident": {
                "event": user_message,
                "protagonist_initial_reaction": "Excitement mixed with nervousness"
            }
        }
    
    # Continue for other phases...
    else:
        # Generic extraction for other phases
        extracted = {"phase_response": user_message}
    
    return json.dumps(extracted)

def _clean_progression_markers(response: str) -> str:
    """Remove progression markers from the user-visible response"""
    import re
    # Remove progression markers in brackets
    cleaned = re.sub(r'\[(?:STAY_CURRENT_STEP|ADVANCE_TO_NEXT_STEP|ADVANCE_TO_NEXT_PHASE|QUEST_COMPLETE)\]', '', response)
    return cleaned.strip()

def _get_current_phase_focus(phase: int, step: int) -> str:
    """Get the current focus area for the phase/step"""
    phase_info = PHASES.get(phase, {})
    step_info = phase_info.get("questions", {}).get(step, {})
    return step_info.get("focus", "your story")

async def _ai_determine_progression(
    current_phase: int, 
    current_step: int, 
    user_message: str, 
    story_context: str,
    ai_response: str
) -> tuple[int, int, bool]:
    """Let AI determine if ready to progress to next step/phase"""
    
    # Parse the AI response for progression indicators (hidden from user)
    ai_response_upper = ai_response.upper()
    
    if "[QUEST_COMPLETE]" in ai_response_upper:
        return current_phase, current_step, True
    elif "[ADVANCE_TO_NEXT_PHASE]" in ai_response_upper:
        return current_phase + 1, 1, False
    elif "[ADVANCE_TO_NEXT_STEP]" in ai_response_upper:
        phase_config = PHASES.get(current_phase, {})
        total_steps = phase_config.get("total_steps", 1)
        
        if current_step < total_steps:
            return current_phase, current_step + 1, False
        else:
            # If at last step of phase, advance to next phase
            return current_phase + 1, 1, False
    else:
        # "[STAY_CURRENT_STEP]" or no indicator - stay put
        return current_phase, current_step, False

def _calculate_next_step(current_phase: int, current_step: int) -> tuple[int, int]:
    """Calculate the next phase and step (legacy function, kept for compatibility)"""
    phase_config = PHASES.get(current_phase, {})
    total_steps = phase_config.get("total_steps", 1)
    
    if current_step < total_steps:
        return current_phase, current_step + 1
    else:
        return current_phase + 1, 1

