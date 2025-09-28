# /ai_rag_story_app/app/routers/views_prompt.py

from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse 
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

# --- Core Application Imports ---
from app.core.deps import get_db_session
from app.core.deps import get_current_active_user
from app.core import security as core_security 
from app.crud import user as crud_user 
from app.models.user import User
from app.models.prompt import PromptTypeEnum, AgeTargetEnum, Prompt as ModelPrompt 
from app.crud import prompt as crud_prompt 
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# --- Router Setup ---
router = APIRouter(
    prefix="/ui/prompts", 
    tags=["ui-prompt-views"]
)

templates = Jinja2Templates(directory="app/templates")

async def get_optional_current_user_for_prompt_views(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Get current user for prompt views, return None if not authenticated."""
    token = request.cookies.get("access_token")
    if not token:
        logger.debug("No access_token cookie found in request for prompt views.")
        return None
    try:
        payload: Optional[dict] = await core_security.decode_access_token(token=token)
        if payload is None:
            logger.warning("Token decoding returned None for prompt views.")
            return None
        username_from_payload: Optional[str] = payload.get("sub")
        if username_from_payload is None:
            logger.warning("Username (sub) not found in token payload for prompt views.")
            return None
    except core_security.JWTError as e: 
        logger.warning(f"JWTError during token decoding in prompt views: {str(e)}")
        return None
    except Exception as e_unhandled: 
        logger.error(f"Unexpected error processing token in prompt views: {e_unhandled}", exc_info=True)
        return None
    
    user = await crud_user.get_user_by_username(db, username=username_from_payload)
    if user is None:
        logger.warning(f"User '{username_from_payload}' from token not found in DB for prompt views.")
        return None
    if not user.is_active: 
        logger.info(f"User '{user.username}' is inactive, treating as no current user for prompt views.")
        return None
    logger.debug(f"User '{user.username}' successfully retrieved for prompt views.")
    return user

@router.get("/", response_class=HTMLResponse, name="ui_list_prompts")
async def list_prompts_ui(
    request: Request,
    filter_prompt_type_str: Optional[str] = Query(None, alias="filter_prompt_type", description="Filter prompts by their type (string value of enum e.g. GENERAL)"),
    filter_age_target_str: Optional[str] = Query(None, alias="filter_age_target", description="Filter prompts by age target (string value of enum e.g. ALL_AGES)"),
    filter_is_active_str: Optional[str] = Query(None, alias="filter_is_active", description="Filter by active status ('true', 'false', or empty for any/all)"),
    filter_scope: Optional[str] = Query("shared", description="Scope of prompts ('my' or 'shared')"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user_for_prompt_views)
):
    logger.info(f"User {current_user.username if current_user else 'Anonymous'} requesting /ui/prompts with filters: type_str='{filter_prompt_type_str}', age_target_str='{filter_age_target_str}', active_str='{filter_is_active_str}', scope='{filter_scope}'")

    actual_filter_prompt_type: Optional[PromptTypeEnum] = None
    if filter_prompt_type_str:
        try:
            actual_filter_prompt_type = PromptTypeEnum(filter_prompt_type_str.upper())
        except ValueError:
            logger.warning(f"Invalid prompt_type filter value received: '{filter_prompt_type_str}'. Ignoring type filter.")
            pass

    actual_filter_age_target: Optional[AgeTargetEnum] = None
    if filter_age_target_str:
        try:
            actual_filter_age_target = AgeTargetEnum(filter_age_target_str.upper())
        except ValueError:
            logger.warning(f"Invalid age_target filter value received: '{filter_age_target_str}'. Ignoring age_target filter.")
            pass

    actual_filter_is_active: Optional[bool] = None
    if filter_is_active_str:
        if filter_is_active_str.lower() == 'true':
            actual_filter_is_active = True
        elif filter_is_active_str.lower() == 'false':
            actual_filter_is_active = False

    prompts: List[ModelPrompt] = []
    
    # For anonymous users, force scope to "shared" and show demo prompts
    if not current_user:
        effective_scope = "shared"
        logger.info("Anonymous user accessing demo prompts.")
        # Show demo/example prompts for anonymous users
        demo_prompts = [
            {
                "id": 1,
                "title": "Fantasy Adventure Starter",
                "prompt_type": "STORY_GENERATION",
                "age_target": "ALL_AGES",
                "content": "Create an engaging fantasy adventure story featuring a young hero who discovers they have magical abilities. Include: a mentor figure, a quest with clear stakes, interesting magical creatures, and a satisfying resolution that shows character growth.",
                "is_active": True,
                "is_shared": True,
                "user_id": None,
                "is_demo": True
            },
            {
                "id": 2,
                "title": "Character Development Deep Dive",
                "prompt_type": "CHARACTER_DEVELOPMENT",
                "age_target": "TEEN_ADULT",
                "content": "Develop a complex character with: clear motivations and fears, a distinctive voice and speech pattern, meaningful relationships with other characters, internal conflicts that drive the plot, and a character arc that shows genuine growth or change.",
                "is_active": True,
                "is_shared": True,
                "user_id": None,
                "is_demo": True
            },
            {
                "id": 3,
                "title": "World Building Foundation",
                "prompt_type": "WORLD_BUILDING",
                "age_target": "ALL_AGES",
                "content": "Create a richly detailed fictional world including: geography and climate, political systems and social structures, cultural traditions and beliefs, technology or magic systems, historical events that shaped the world, and how these elements affect daily life.",
                "is_active": True,
                "is_shared": True,
                "user_id": None,
                "is_demo": True
            }
        ]
        
        return templates.TemplateResponse(
            "pages/prompts_list.html",
            {
                "request": request,
                "prompts": demo_prompts,
                "current_user": current_user,
                "effective_scope": effective_scope,
                "filter_prompt_type": filter_prompt_type_str,
                "filter_age_target": filter_age_target_str,
                "filter_is_active": filter_is_active_str,
                "all_prompt_types": list(PromptTypeEnum),
                "all_age_targets": list(AgeTargetEnum)
            }
        )
    
    effective_scope = filter_scope if filter_scope in ["my", "shared"] else "my"

    if effective_scope == "my":
        prompts = await crud_prompt.get_prompts_by_user(
            db,
            user_id=current_user.id,
            prompt_type=actual_filter_prompt_type,
            age_target=actual_filter_age_target,
            is_active=actual_filter_is_active
        )
    else: # shared
        is_active_for_shared_query = True if actual_filter_is_active is None else actual_filter_is_active
        prompts = await crud_prompt.get_shared_prompts(
            db,
            prompt_type=actual_filter_prompt_type,
            age_target=actual_filter_age_target,
            is_active=is_active_for_shared_query
        )
    logger.info(f"Fetched {len(prompts)} prompts for scope '{effective_scope}'.")

    prompt_types_for_filter = [ptype for ptype in PromptTypeEnum]
    # --- FIX: Add age_targets_for_filter to the context ---
    age_targets_for_filter = [age_target for age_target in AgeTargetEnum]

    return templates.TemplateResponse(
        "pages/prompt_list.html",
        {
            "request": request,
            "prompts": prompts,
            "current_user": current_user,
            "prompt_types": prompt_types_for_filter,
            "age_targets": age_targets_for_filter, # <-- PASS THE VARIABLE TO THE TEMPLATE
            "current_filters": { 
                "prompt_type": actual_filter_prompt_type.value if actual_filter_prompt_type else None,
                "age_target": actual_filter_age_target.value if actual_filter_age_target else None,
                "is_active_str": filter_is_active_str, 
                "scope": effective_scope
            }
        }
    )

@router.get("/new", response_class=HTMLResponse, name="ui_create_prompt_form")
async def create_prompt_ui_form(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User {current_user.username} accessing create new prompt form.")
    prompt_types_for_form = [ptype for ptype in PromptTypeEnum]
    age_targets_for_form = [age for age in AgeTargetEnum]
    return templates.TemplateResponse(
        "pages/prompt_form.html",
        {
            "request": request,
            "prompt": None, 
            "current_user": current_user,
            "prompt_types": prompt_types_for_form, 
            "age_targets": age_targets_for_form,
            "form_action_url": request.url_for('create_new_prompt') 
        }
    )

@router.get("/{prompt_id}/edit", response_class=HTMLResponse, name="ui_edit_prompt_form")
async def edit_prompt_ui_form(
    request: Request,
    prompt_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User {current_user.username} accessing edit form for prompt ID: {prompt_id}")
    prompt = await crud_prompt.get_prompt(db, prompt_id=prompt_id)
    if not prompt:
        logger.warning(f"Prompt ID {prompt_id} not found for editing by user {current_user.username}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    if prompt.user_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to edit prompt ID {prompt_id} owned by user ID {prompt.user_id}.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this prompt")

    prompt_types_for_form = [ptype for ptype in PromptTypeEnum]
    age_targets_for_form = [age for age in AgeTargetEnum]
    return templates.TemplateResponse(
        "pages/prompt_form.html", 
        {
            "request": request,
            "prompt": prompt, 
            "current_user": current_user,
            "prompt_types": prompt_types_for_form,
            "age_targets": age_targets_for_form,
            "form_action_url": request.url_for('update_existing_prompt', prompt_id=prompt.id) 
        }
    )