"""API routes for views story wizard."""

# /story_app/app/routers/views_story_wizard.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import logging
import json
import uuid
from datetime import UTC, datetime, timedelta

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.core.config import settings
from app.services.ai_model_cache import model_cache
from app.crud import user as crud_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ui/story-wizard",
    tags=["ui-story-wizard"],
)

@router.get("/health", response_class=HTMLResponse)
async def story_wizard_health():
    """Health check for Story Wizard"""
    try:
        # Test model cache
        ai_models = model_cache.get_generation_models_list()
        
        # Test template loading
        templates_status = "OK"
        
        # Test imports
        from app.services.langgraph_runtime_setup import kernel
        kernel_status = "OK" if kernel else "Not available"
        
        return {
            "status": "healthy",
            "ai_models_count": len(ai_models),
            "templates": templates_status,
            "kernel": kernel_status
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Create templates instance
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["google_analytics_id"] = settings.GOOGLE_ANALYTICS_ID
templates.env.globals["google_analytics_consent_mode"] = settings.GOOGLE_ANALYTICS_CONSENT_MODE
templates.env.globals["cookie_consent_required"] = settings.COOKIE_CONSENT_REQUIRED

# In-memory session storage (for MVP - should use Redis in production)
wizard_sessions: Dict[str, Dict[str, Any]] = {}

@router.get("/", response_class=HTMLResponse)
async def story_wizard_page(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Display the Story Wizard chat interface
    """
    try:
        logger.info(f"Story Wizard page accessed by user {current_user.id}")
        
        # Check if user has sufficient credits
        # For now, skip the credit check until billing system is properly configured
        # TODO: Implement proper credit checking when billing system is ready
        logger.info(f"User {current_user.id} accessing Story Wizard (credit check temporarily disabled)")

        # Create a new session ID for this wizard instance
        session_id = str(uuid.uuid4())
        
        # Store session with expiry
        wizard_sessions[session_id] = {
            "user_id": current_user.id,
            "created_at": datetime.now(UTC),
            "expires_at": datetime.now(UTC) + timedelta(days=1),
            "phase": 1,
            "step": 1,
            "conversation": [],
            "story_data": {
                "core_concept": "",
                "genre": "",
                "mood_atmosphere": "",
                "protagonist": {},
                "setting": {},
                "inciting_incident": {},
                "antagonist": {},
                "conflicts": {},
                "relationships": [],
                "plot_points": {},
                "resolution": {},
                "theme": ""
            }
        }

        # Get available AI models for the user
        try:
            ai_models = model_cache.get_generation_models_list()
            logger.info(f"Loaded {len(ai_models)} AI models for user {current_user.id}")
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
            ai_models = []

        logger.info(f"Returning Story Wizard template for user {current_user.id}")
        return templates.TemplateResponse(
            "pages/story_wizard.html",
            {
                "request": request,
                "current_user": current_user,
                "session_id": session_id,
                "ai_models": ai_models,
                "phases": [
                    {"id": 1, "name": "Core Spark & Protagonist", "steps": 2},
                    {"id": 2, "name": "World & Call to Adventure", "steps": 2},
                    {"id": 3, "name": "Conflict, Stakes & Supporting Cast", "steps": 3},
                    {"id": 4, "name": "Climax, Resolution & Theme", "steps": 2}
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error loading Story Wizard page: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "pages/story_wizard.html",
            {
                "request": request,
                "current_user": current_user,
                "error": f"Unable to load Story Wizard: {str(e)}",
                "ai_models": [],
                "phases": []
            }
        )

@router.post("/chat")
async def story_wizard_chat(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Handle chat messages in the Story Wizard
    """
    try:
        data = await request.json()
        session_id = data.get("session_id")
        message = data.get("message")
        ai_model_id = data.get("ai_model_id")

        # Validate session
        if session_id not in wizard_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired"
            )

        session = wizard_sessions[session_id]
        
        # Check session expiry
        if datetime.now(UTC) > session["expires_at"]:
            del wizard_sessions[session_id]
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Session expired"
            )

        # Check user ownership
        if session["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized session access"
            )

        # Add user message to conversation
        session["conversation"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(UTC).isoformat()
        })

        # Generate AI response using the story wizard prompt
        ai_response, token_usage = await _generate_wizard_response(
            db, current_user, session, ai_model_id
        )

        # Add AI response to conversation
        session["conversation"].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now(UTC).isoformat()
        })

        # Extract and update story data
        updated_story_data = await _extract_story_data(session, message)

        # Check if we should advance to next step
        next_phase, next_step = _calculate_next_step(session)
        session["phase"] = next_phase
        session["step"] = next_step

        # Check if wizard is complete
        is_complete = next_phase > 4

        return JSONResponse({
            "success": True,
            "response": ai_response,
            "phase": next_phase,
            "step": next_step,
            "story_data": updated_story_data,
            "is_complete": is_complete,
            "token_usage": token_usage
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Story Wizard chat: {str(e)}")
        
        # Refund coins on error  
        if current_user and 'token_usage' in locals() and token_usage:
            await crud_user.add_coins(db, current_user.id, int(token_usage.get('cost', 0)))
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message"
        )

@router.post("/generate-report")
async def generate_story_report(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate the final story report in text and JSON formats
    """
    try:
        data = await request.json()
        session_id = data.get("session_id")

        # Validate session
        if session_id not in wizard_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        session = wizard_sessions[session_id]
        story_data = session["story_data"]

        # Generate formatted text report
        text_report = _format_story_text_report(story_data)

        # Clean up session after report generation
        del wizard_sessions[session_id]

        return JSONResponse({
            "success": True,
            "text_report": text_report,
            "json_report": story_data
        })

    except Exception as e:
        logger.error(f"Error generating story report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate story report"
        )

# Helper functions
async def _generate_wizard_response(
    db: AsyncSession, 
    user: User, 
    session: Dict[str, Any],
    ai_model_id: Optional[int] = None
) -> tuple[str, dict]:
    """Generate AI response for the wizard"""
    from app.routers.story_wizard_api import process_wizard_message
    
    # Call the API function directly
    result = await process_wizard_message(
        request_data={
            "session_data": session,
            "message": session["conversation"][-1]["content"],  # Last user message
            "ai_model_id": ai_model_id
        },
        db=db,
        current_user=user
    )
    
    # Update session with new story data
    session["story_data"] = result["story_data"]
    
    return result["response"], result["token_usage"]

def _build_wizard_system_prompt(session: Dict[str, Any]) -> str:
    """Build the system prompt for the current phase/step"""
    base_prompt = """You are an advanced "Story Idea Wizard" AI, capable of guiding a writer through the comprehensive development of a story's foundational elements. Your ultimate goal is to help the user construct a detailed "Text Frame" – a structured outline covering core story components.

Important: Keep your responses concise and focused. Ask only one question at a time. Avoid lengthy explanations.

Current Phase: {phase_name}
Current Step: {step} of {total_steps}

Your process:
1. Briefly introduce the current phase/step
2. Ask ONE focused question
3. Wait for the user's response
4. Be encouraging but concise

Accumulated story data so far:
{story_data}
"""
    
    phase_names = {
        1: "Core Spark & Protagonist",
        2: "World & Call to Adventure",
        3: "Conflict, Stakes & Supporting Cast", 
        4: "Climax, Resolution & Theme"
    }
    
    phase_steps = {1: 2, 2: 2, 3: 3, 4: 2}
    
    return base_prompt.format(
        phase_name=phase_names.get(session["phase"], "Unknown"),
        step=session["step"],
        total_steps=phase_steps.get(session["phase"], 1),
        story_data=json.dumps(session["story_data"], indent=2)
    )

async def _extract_story_data(session: Dict[str, Any], user_message: str) -> Dict[str, Any]:
    """Extract and update story data from user response"""
    # This is a placeholder - implement actual extraction logic
    # In production, use AI to extract structured data from the conversation
    return session["story_data"]

def _calculate_next_step(session: Dict[str, Any]) -> tuple[int, int]:
    """Calculate the next phase and step"""
    phase_steps = {1: 2, 2: 2, 3: 3, 4: 2}
    
    current_phase = session["phase"]
    current_step = session["step"]
    
    if current_step < phase_steps.get(current_phase, 1):
        return current_phase, current_step + 1
    else:
        return current_phase + 1, 1

def _format_story_text_report(story_data: Dict[str, Any]) -> str:
    """Format the story data into a readable text report"""
    report = f"""
Story Text Frame: {story_data.get('story_title', 'Untitled Story')}

Core Spark & Protagonist
------------------------
Core Concept: {story_data.get('core_concept', '')}
Genre: {story_data.get('genre', '')}
Mood/Atmosphere: {story_data.get('mood_atmosphere', '')}

Protagonist: {story_data.get('protagonist', {}).get('name', '')}
- Age: {story_data.get('protagonist', {}).get('age', '')}
- Defining Characteristic: {story_data.get('protagonist', {}).get('defining_characteristic', '')}
- Initial Desire/Goal: {story_data.get('protagonist', {}).get('initial_desire_goal', '')}
- Primary Flaw/Weakness: {story_data.get('protagonist', {}).get('primary_flaw_weakness', '')}

The World & The Call to Adventure
---------------------------------
Primary Setting: {story_data.get('setting', {}).get('primary_location', '')}
Unique Rules/Characteristics:
{_format_list(story_data.get('setting', {}).get('unique_rules_characteristics', []))}

Societal/Cultural Atmosphere:
{_format_dict(story_data.get('setting', {}).get('societal_cultural_atmosphere', {}))}

Inciting Incident: {story_data.get('inciting_incident', {}).get('event', '')}
Protagonist's Initial Reaction: {story_data.get('inciting_incident', {}).get('protagonist_initial_reaction', '')}

Conflict, Stakes, and Supporting Cast
------------------------------------
Primary Antagonist: {story_data.get('antagonist', {}).get('description', '')}
Antagonist's Goal/Motivation: {story_data.get('antagonist', {}).get('goal_motivation', '')}

Significant External Obstacles:
{_format_list(story_data.get('major_conflicts', {}).get('external_obstacles', []))}

Personal Stakes: {story_data.get('major_conflicts', {}).get('personal_stakes', '')}
Broader Consequences: {story_data.get('major_conflicts', {}).get('broader_consequences', '')}

Key Relationships:
{_format_relationships(story_data.get('key_relationships', []))}

Climax, Resolution, and Theme
-----------------------------
Mid-point Turning Point: {story_data.get('plot_points', {}).get('mid_point_turning_point', '')}
Climax Description: {story_data.get('plot_points', {}).get('climax_description', '')}
Protagonist's Growth in Climax: {story_data.get('plot_points', {}).get('protagonist_growth_in_climax', '')}

Resolution: {story_data.get('resolution', {}).get('outcome_for_protagonist_world', '')}
Ending Tone: {story_data.get('resolution', {}).get('ending_tone', '')}

Central Theme: {story_data.get('theme', '')}
"""
    return report.strip()

def _format_list(items: list) -> str:
    """Format a list for the text report"""
    if not items:
        return "- None specified"
    return "\n".join(f"- {item}" for item in items)

def _format_dict(data: dict) -> str:
    """Format a dictionary for the text report"""
    if not data:
        return "- None specified"
    return "\n".join(f"- {key}: {value}" for key, value in data.items())

def _format_relationships(relationships: list) -> str:
    """Format relationships for the text report"""
    if not relationships:
        return "- None specified"
    
    formatted = []
    for rel in relationships:
        formatted.append(f"- {rel.get('name', 'Unknown')} ({rel.get('type', 'Unknown')})")
        formatted.append(f"  Role: {rel.get('role', '')}")
        formatted.append(f"  Unique Skill/Perspective: {rel.get('unique_skill_perspective', '')}")
        if 'how_it_changes' in rel:
            formatted.append(f"  How it Changes: {rel.get('how_it_changes', '')}")
    
    return "\n".join(formatted)
