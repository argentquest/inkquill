from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import logging

from app.core.deps import get_db_session, get_current_active_user
from app.core import security as core_security 
from app.crud import user as crud_user
from app.models.user import User
from app.models.brainstorm_session import BrainstormSession, BrainstormFavorite, BrainstormStory
from app.models.user_interview_response import UserInterviewResponse
from app.services.story_brainstorm_service import StoryBrainstormService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui/brainstorm", tags=["brainstorm"])
templates = Jinja2Templates(directory="app/templates")

async def get_optional_current_user_for_brainstorm_views(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Get current user for brainstorm views, return None if not authenticated."""
    token = request.cookies.get("access_token")
    if not token:
        logger.debug("No access_token cookie found in request for brainstorm views.")
        return None
    try:
        payload: Optional[dict] = await core_security.decode_access_token(token=token)
        if payload is None:
            logger.warning("Token decoding returned None for brainstorm views.")
            return None
        username_from_payload: Optional[str] = payload.get("sub")
        if username_from_payload is None:
            logger.warning("Username (sub) not found in token payload for brainstorm views.")
            return None
    except core_security.JWTError as e: 
        logger.warning(f"JWTError during token decoding in brainstorm views: {str(e)}")
        return None
    except Exception as e_unhandled: 
        logger.error(f"Unexpected error processing token in brainstorm views: {e_unhandled}", exc_info=True)
        return None
    
    user = await crud_user.get_user_by_username(db, username=username_from_payload)
    if user is None:
        logger.warning(f"User '{username_from_payload}' from token not found in DB for brainstorm views.")
        return None
    if not user.is_active: 
        logger.info(f"User '{user.username}' is inactive, treating as no current user for brainstorm views.")
        return None
    logger.debug(f"User '{user.username}' successfully retrieved for brainstorm views.")
    return user


# Request/Response Models
class GenerateConceptsRequest(BaseModel):
    interview_response_id: int

class SaveFavoriteRequest(BaseModel):
    session_id: int
    concept_id: str

class CreateStoryRequest(BaseModel):
    favorite_id: int


@router.get("/", response_class=HTMLResponse)
async def brainstorm_page(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user_for_brainstorm_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Main brainstorm page - shows concept, start button, and existing favorites"""
    
    if current_user:
        # Get user's existing brainstorm sessions
        sessions_result = await db.execute(
            select(BrainstormSession)
            .filter(BrainstormSession.user_id == current_user.id)
            .order_by(desc(BrainstormSession.created_at))
        )
        sessions = sessions_result.scalars().all()
        
        # Get user's favorites across all sessions
        favorites_result = await db.execute(
            select(BrainstormFavorite)
            .filter(BrainstormFavorite.user_id == current_user.id)
            .order_by(desc(BrainstormFavorite.created_at))
        )
        favorites = favorites_result.scalars().all()
    else:
        logger.info("Anonymous user accessing demo brainstorm page.")
        # For anonymous users, show demo/example content
        sessions = []
        favorites = [
            {
                "id": 1,
                "concept_title": "The Quantum Detective",
                "concept_summary": "A detective who can observe multiple timelines to solve crimes that haven't happened yet",
                "generated_concept": {
                    "title": "The Quantum Detective",
                    "premise": "Detective Sarah Chen discovers she can perceive quantum possibilities, allowing her to see potential crimes before they occur. But changing the future comes with unexpected consequences.",
                    "genre": "Science Fiction Mystery",
                    "setting": "Near-future metropolis where quantum computing has revolutionized crime prevention"
                },
                "is_demo": True
            },
            {
                "id": 2, 
                "concept_title": "Songs of the Deep Forest",
                "concept_summary": "A world where ancient trees hold the memories of civilizations and sing their stories to those who know how to listen",
                "generated_concept": {
                    "title": "Songs of the Deep Forest",
                    "premise": "Young botanist Maya discovers that the ancient redwoods in her research area are actually living archives, storing the collective memory of lost civilizations in their rings. When developers threaten the grove, she must learn the trees' ancient language to preserve their stories.",
                    "genre": "Fantasy Environmental",
                    "setting": "Modern-day Pacific Northwest with hidden magical elements"
                },
                "is_demo": True
            }
        ]
    
    return templates.TemplateResponse(
        "pages/brainstorm.html",
        {
            "request": request,
            "user": current_user,
            "sessions": sessions,
            "favorites": favorites,
            "has_favorites": len(favorites) > 0,
            "project_name": "AI Story Assistant"
        }
    )


@router.get("/api/sessions", response_model=List[dict])
async def get_brainstorm_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all brainstorm sessions for the current user"""
    
    result = await db.execute(
        select(BrainstormSession)
        .filter(BrainstormSession.user_id == current_user.id)
        .order_by(desc(BrainstormSession.created_at))
    )
    sessions = result.scalars().all()
    
    return [
        {
            "id": session.id,
            "session_name": session.session_name,
            "created_at": session.created_at.isoformat(),
            "concepts": session.get_concepts(),
            "concept_count": len(session.get_concepts())
        }
        for session in sessions
    ]


@router.get("/api/favorites", response_model=List[dict])
async def get_brainstorm_favorites(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all favorite concepts for the current user"""
    
    result = await db.execute(
        select(BrainstormFavorite)
        .filter(BrainstormFavorite.user_id == current_user.id)
        .order_by(desc(BrainstormFavorite.created_at))
    )
    favorites = result.scalars().all()
    
    return [
        {
            "id": favorite.id,
            "session_id": favorite.session_id,
            "concept_id": favorite.concept_id,
            "concept_data": favorite.get_concept_data(),
            "is_selected": favorite.is_selected,
            "created_at": favorite.created_at.isoformat()
        }
        for favorite in favorites
    ]


@router.post("/api/generate-concepts")
async def generate_story_concepts(
    request: GenerateConceptsRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate 15 story concepts based on interview responses"""
    
    user_id = current_user.id  # Capture user ID early to avoid database access issues in error handling
    
    try:
        service = StoryBrainstormService()
        result = await service.generate_story_concepts(
            user=current_user,
            interview_response_id=request.interview_response_id,
            db=db
        )
        return result
        
    except Exception as e:
        logger.error(f"Error generating concepts for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/save-favorite")
async def save_favorite_concept(
    request: SaveFavoriteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Save a story concept as favorite"""
    
    user_id = current_user.id  # Capture user ID early to avoid database access issues in error handling
    
    try:
        service = StoryBrainstormService()
        favorite = await service.save_favorite_concept(
            user=current_user,
            session_id=request.session_id,
            concept_id=request.concept_id,
            db=db
        )
        
        # Check if this is the user's first saved favorite and award Step 2 bonus
        if not current_user.bonus2:
            logger.info(f"Automatically awarding Step 2 bonus to user {current_user.id} for first brainstorm favorite")
            
            # Import required modules for bonus awarding
            from decimal import Decimal
            from app.crud.billing import billing_crud
            from app.schemas.billing import UserTransactionCreate
            from app.models.user_transaction import TransactionType
            
            # Mark Step 2 bonus as claimed
            current_user.bonus2 = True
            
            # Award 50 coins for completing brainstorm
            coins_to_award = Decimal('50.0000')
            account = await billing_crud.get_or_create_user_account(db, current_user.id)
            new_balance = account.current_balance + coins_to_award
            
            # Create step bonus transaction
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.STEP_BONUS,
                amount=coins_to_award,
                balance_after=new_balance,
                description="Step Bonus: Story Brainstorm - 50 Coins",
                transaction_metadata={"step_number": 2, "step_name": "Story Brainstorm", "auto_awarded": True}
            )
            
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and total credits added
            account.current_balance = new_balance
            account.total_credits_added += coins_to_award
            
            # Commit the bonus update
            await db.commit()
            await db.refresh(current_user)
            
            logger.info(f"Awarded 50 coins to user {current_user.id} for completing story brainstorm")
            bonus_awarded = True
        else:
            bonus_awarded = False
        
        return {
            "id": favorite.id,
            "concept_id": favorite.concept_id,
            "created_at": favorite.created_at.isoformat(),
            "concept_data": favorite.get_concept_data(),
            "bonus_awarded": bonus_awarded  # Let frontend know if bonus was awarded
        }
        
    except Exception as e:
        logger.error(f"Error saving favorite for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/favorite/{favorite_id}")
async def remove_favorite_concept(
    favorite_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Remove a concept from favorites"""
    
    user_id = current_user.id  # Capture user ID early to avoid database access issues in error handling
    
    try:
        service = StoryBrainstormService()
        success = await service.remove_favorite_concept(
            user=current_user,
            favorite_id=favorite_id,
            db=db
        )
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Error removing favorite for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/create-story")
async def create_three_act_story(
    request: CreateStoryRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate three-act story structure from favorite concept"""
    
    user_id = current_user.id  # Capture user ID early to avoid database access issues in error handling
    
    try:
        service = StoryBrainstormService()
        result = await service.generate_three_act_story(
            user=current_user,
            favorite_id=request.favorite_id,
            db=db
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating story for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))