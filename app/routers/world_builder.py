"""World Builder API Router

Handles the world building wizard API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.world import World
from app.services.world_builder_service import world_builder_service
from app.schemas.world import WorldRead
from app.schemas.base import ApiResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas for request/response
class WorldBuilderQuestion(BaseModel):
    """Schema for a world builder question"""
    id: int
    short_label: str
    full_question: str
    answers: List[Dict[str, Any]]


class WorldBuilderQuestionsResponse(BaseModel):
    """Schema for questions list response"""
    questions: List[WorldBuilderQuestion]


class WorldBuilderAnswersRequest(BaseModel):
    """Schema for submitting answers"""
    answers: Dict[int, int] = Field(
        ..., 
        description="Mapping of question_id to answer_id"
    )


class WorldBuilderGenerationRequest(BaseModel):
    """Schema for generating world description from answers"""
    answers: Dict[int, int] = Field(
        ..., 
        description="Mapping of question_id to answer_id"
    )


class WorldBuilderGenerationResponse(BaseModel):
    """Schema for generated world descriptions"""
    short_description: str
    description: str
    visual_prompt: str
    answer_summary: List[Dict[str, str]]


class WorldBuilderCreateRequest(BaseModel):
    """Schema for creating a world from builder"""
    name: str = Field(..., min_length=1, max_length=255)
    answers: Dict[int, int] = Field(
        ..., 
        description="Mapping of question_id to answer_id"
    )


@router.get(
    "/questions",
    response_model=ApiResponse,
    summary="Get all world builder questions"
)
async def get_world_builder_questions(
    current_user: User = Depends(get_current_user)
):
    """
    Get all available world builder questions and their answer options.
    """
    try:
        questions = world_builder_service.get_all_questions()
        
        # Convert to response format
        question_objects = [
            WorldBuilderQuestion(
                id=q["id"],
                short_label=q["short_label"],
                full_question=q["full_question"],
                answers=q["answers"]
            )
            for q in questions
        ]
        
        return WorldBuilderQuestionsResponse(questions=question_objects)
        
    except Exception as e:
        logger.error(f"Failed to get world builder questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load world builder questions"
        )


@router.get(
    "/questions/{question_id}",
    response_model=ApiResponse,
    summary="Get a specific world builder question"
)
async def get_world_builder_question(
    question_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific world builder question by ID.
    """
    question = world_builder_service.get_question_by_id(question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_id} not found"
        )
    
    return WorldBuilderQuestion(
        id=question["id"],
        short_label=question["short_label"],
        full_question=question["full_question"],
        answers=question["answers"]
    )


@router.post(
    "/validate",
    summary="Validate world builder answers"
)
async def validate_world_builder_answers(
    request: WorldBuilderAnswersRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate that the provided answers are valid for the world builder questions.
    """
    is_valid, errors = world_builder_service.validate_answers(request.answers)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "answer_count": len(request.answers)
    }


@router.post(
    "/generate",
    response_model=ApiResponse,
    summary="Generate world description from answers"
)
async def generate_world_description(
    request: WorldBuilderGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Generate AI world descriptions (short and long) from user answers.
    """
    try:
        # Validate answers first
        is_valid, errors = world_builder_service.validate_answers(request.answers)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid answers: {', '.join(errors)}"
            )
        
        # Generate world descriptions
        generated_content = await world_builder_service.generate_world_description(
            answers=request.answers,
            user_id=current_user.id,
            db=db
        )
        
        # Get answer summary for preview
        answer_summary = world_builder_service.get_answer_summary(request.answers)
        
        return WorldBuilderGenerationResponse(
            short_description=generated_content["short_description"],
            description=generated_content["description"],
            visual_prompt=generated_content["visual_prompt"],
            answer_summary=answer_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate world description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate world description"
        )


@router.post(
    "/create",
    response_model=ApiResponse,
    summary="Create a new world from world builder"
)
async def create_world_from_builder(
    request: WorldBuilderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new world from world builder answers and generated descriptions.
    """
    try:
        # Validate answers first
        is_valid, errors = world_builder_service.validate_answers(request.answers)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid answers: {', '.join(errors)}"
            )
        
        # Generate world descriptions
        generated_content = await world_builder_service.generate_world_description(
            answers=request.answers,
            user_id=current_user.id,
            db=db
        )
        
        # Create the world
        world = await world_builder_service.create_world_from_builder(
            user_id=current_user.id,
            world_name=request.name,
            answers=request.answers,
            generated_content=generated_content,
            db=db
        )
        
        # Convert to response format
        world_response = WorldRead.from_orm(world)
        return world_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create world from builder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create world from builder"
        )


@router.put(
    "/worlds/{world_id}",
    response_model=ApiResponse,
    summary="Update existing world with world builder"
)
async def update_world_from_builder(
    world_id: int,
    request: WorldBuilderGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update an existing world with new world builder data.
    """
    try:
        # Check if world exists and user has access
        from app.crud import world as crud_world
        world = await crud_world.get_world(db, world_id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found"
            )
        
        if world.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this world"
            )
        
        # Validate answers
        is_valid, errors = world_builder_service.validate_answers(request.answers)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid answers: {', '.join(errors)}"
            )
        
        # Generate new descriptions
        generated_content = await world_builder_service.generate_world_description(
            answers=request.answers,
            user_id=current_user.id,
            db=db
        )
        
        # Update the world
        updated_world = await world_builder_service.update_world_from_builder(
            world_id=world_id,
            answers=request.answers,
            generated_content=generated_content,
            db=db
        )
        
        # Convert to response format
        world_response = WorldRead.from_orm(updated_world)
        return world_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update world from builder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update world from builder"
        )