"""API routes for interview."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

from app.core.deps import get_db_session, get_current_active_user
from app.models.user_interview_response import UserInterviewResponse
from app.models.user import User
from app.services.interview_validation_service import validation_service
from app.schemas.base import ApiResponse
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/v1/interview", tags=["interview"])


class InterviewSubmissionRequest(BaseModel):
    """Response or helper model for interview submission request."""
    interview_id: str = Field(..., description="ID of the interview being completed")
    responses: Dict[str, Any] = Field(..., description="User responses to all questions")
    navigation: Dict[str, Any] = Field(..., description="Navigation result from responses")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Completion metadata")


class InterviewSubmissionResponse(BaseModel):
    """Response or helper model for interview submission response."""
    success: bool
    interview_id: int
    message: str


@router.get("/questions/{interview_id}")
async def get_interview_questions(interview_id: str):
    """Get the questions for a specific interview with schema validation"""
    logger.info(f"GET /questions/{interview_id} - Loading interview questions for: {interview_id}")
    
    questions_file = Path(__file__).parent.parent / "data" / "interviews" / f"{interview_id}.json"
    logger.info(f"Looking for questions file at: {questions_file}")
    
    if not questions_file.exists():
        logger.error(f"Interview questions file not found: {questions_file}")
        raise HTTPException(
            status_code=404,
            detail="Interview questions file not found"
        )
    
    try:
        logger.info("Reading questions file...")
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        logger.info(f"Loaded questions data. Interview ID in file: {questions_data.get('interview_id')}")
        logger.info(f"Number of questions: {len(questions_data.get('questions', []))}")
        
        # Validate questions against schema
        logger.info("Starting schema validation...")
        validation_service.validate_questions(questions_data)
        logger.info("Schema validation passed!")
        
        # Verify the interview ID matches
        if questions_data.get("interview_id") != interview_id:
            logger.warning(f"Interview ID mismatch: requested '{interview_id}', found '{questions_data.get('interview_id')}'")
            raise HTTPException(
                status_code=404,
                detail=f"Interview '{interview_id}' not found"
            )
        
        logger.info(f"Successfully loaded and validated questions for interview: {interview_id}")
        logger.info(f"Returning {len(questions_data.get('questions', []))} questions to client")
        return questions_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in questions file: {e}")
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON in questions file"
        )
    except HTTPException as he:
        # Re-raise HTTPExceptions (like validation errors) with more detail
        logger.error(f"HTTPException in get_interview_questions: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading questions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error loading questions: {str(e)}"
        )


@router.post("/submit", response_model=ApiResponse)
async def submit_interview(
    submission: InterviewSubmissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Submit completed interview responses with comprehensive validation"""
    
    logger.info(f"Submitting interview {submission.interview_id} for user {current_user.id}")
    
    # Check if user already has a response for this interview
    # For story_brainstorm interviews, always create new records (allow multiple brainstorm sessions)
    # For other interviews, allow retaking (update existing response)
    existing_response = None
    
    if submission.interview_id != "story_brainstorm":
        result = await db.execute(
            select(UserInterviewResponse).filter(
                UserInterviewResponse.user_id == current_user.id,
                UserInterviewResponse.interview_id == submission.interview_id
            )
        )
        existing_response = result.scalar_one_or_none()
        
        if existing_response:
            logger.info(f"User {current_user.id} is retaking interview {submission.interview_id}, will update existing response")
    else:
        logger.info(f"User {current_user.id} is creating new story_brainstorm session (multiple sessions allowed)")
    
    # Build the complete response JSON
    complete_response = {
        "interview_id": submission.interview_id,
        "user_id": current_user.id,
        "completed_at": datetime.utcnow().isoformat(),
        "responses": submission.responses,
        "navigation": submission.navigation,
        "metadata": {
            **submission.metadata,
            "submitted_via": "web_interface",
            "user_agent": submission.metadata.get("user_agent", "unknown")
        }
    }
    
    # Validate response against schema
    try:
        validation_service.validate_response(complete_response)
        logger.info(f"Response schema validation passed for user {current_user.id}")
    except HTTPException as e:
        logger.error(f"Response validation failed for user {current_user.id}: {e.detail}")
        raise
    
    # Cross-validate against questions (optional - warns but doesn't fail)
    try:
        # Load questions for cross-validation
        questions_file = Path(__file__).parent.parent / "data" / "interviews" / f"{submission.interview_id}.json"
        if questions_file.exists():
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
            
            if questions_data.get("interview_id") == submission.interview_id:
                warnings = validation_service.validate_response_against_questions(
                    complete_response, questions_data
                )
                if warnings:
                    logger.warning(f"Cross-validation warnings for user {current_user.id}: {warnings}")
                    # Log warnings but don't fail the submission
                    
    except Exception as e:
        logger.error(f"Error during cross-validation: {e}")
        # Don't fail submission due to cross-validation errors
    
    # Sanitize the response data
    try:
        complete_response = validation_service.sanitize_response(complete_response)
        logger.debug(f"Response data sanitized for user {current_user.id}")
    except Exception as e:
        logger.error(f"Error sanitizing response data: {e}")
        # Continue with original data if sanitization fails
    
    # Create or update the database record
    try:
        if existing_response:
            # Update existing response
            existing_response.json_response = json.dumps(complete_response, ensure_ascii=False, indent=2)
            existing_response.completed_at = datetime.utcnow()
            interview_response = existing_response
            action = "updated"
        else:
            # Create new response
            interview_response = UserInterviewResponse(
                user_id=current_user.id,
                interview_id=submission.interview_id,
                json_response=json.dumps(complete_response, ensure_ascii=False, indent=2),
                completed_at=datetime.utcnow()
            )
            db.add(interview_response)
            action = "created"
        
        await db.commit()
        await db.refresh(interview_response)
        
        logger.info(f"Interview {submission.interview_id} successfully {action} for user {current_user.id} with ID {interview_response.id}")
        
        return ApiResponse.success_response(
            data=InterviewSubmissionResponse(
                success=True,
                interview_id=interview_response.id,
                message=f"Interview {'retaken' if action == 'updated' else 'submitted'} successfully"
            )
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error saving interview for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error saving interview: {str(e)}"
        )


@router.get("/status/{interview_id}")
async def get_interview_status(
    interview_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Check if user has completed a specific interview"""
    
    result = await db.execute(
        select(UserInterviewResponse).filter(
            UserInterviewResponse.user_id == current_user.id,
            UserInterviewResponse.interview_id == interview_id
        )
    )
    response = result.scalar_one_or_none()
    
    return {
        "completed": response is not None,
        "completed_at": response.completed_at.isoformat() if response else None,
        "response_id": response.id if response else None
    }


@router.get("/response/{interview_id}")
async def get_user_interview_response(
    interview_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's response to a specific interview"""
    
    result = await db.execute(
        select(UserInterviewResponse).filter(
            UserInterviewResponse.user_id == current_user.id,
            UserInterviewResponse.interview_id == interview_id
        )
    )
    response = result.scalar_one_or_none()
    
    if not response:
        raise HTTPException(
            status_code=404,
            detail="Interview response not found"
        )
    
    return {
        "id": response.id,
        "interview_id": response.interview_id,
        "completed_at": response.completed_at.isoformat(),
        "response_data": response.get_response_data()
    }


@router.get("/user-insights")
async def get_user_insights(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get insights from user's interview responses for personalization"""
    
    result = await db.execute(
        select(UserInterviewResponse).filter(
            UserInterviewResponse.user_id == current_user.id,
            UserInterviewResponse.interview_id == "new_user_onboarding"
        )
    )
    onboarding_response = result.scalar_one_or_none()
    
    if not onboarding_response:
        return {
            "has_completed_onboarding": False,
            "insights": {}
        }
    
    return {
        "has_completed_onboarding": True,
        "insights": {
            "writing_experience": onboarding_response.get_writing_experience(),
            "preferred_genres": onboarding_response.get_selected_genres(),
            "help_needed": onboarding_response.get_help_needed(),
            "writing_stage": onboarding_response.get_writing_stage(),
            "navigation_choice": onboarding_response.get_navigation_choice(),
            "wants_brainstorming": onboarding_response.wants_brainstorming(),
            "story_summary": onboarding_response.get_story_summary(),
            "navigation_destination": onboarding_response.get_navigation_destination()
        }
    }


@router.get("/story-brainstorm/sessions")
async def get_story_brainstorm_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all story brainstorm sessions for the current user"""
    
    result = await db.execute(
        select(UserInterviewResponse).filter(
            UserInterviewResponse.user_id == current_user.id,
            UserInterviewResponse.interview_id == "story_brainstorm"
        ).order_by(UserInterviewResponse.completed_at.desc())
    )
    sessions = result.scalars().all()
    
    return {
        "sessions": [
            {
                "id": session.id,
                "completed_at": session.completed_at.isoformat(),
                "response_data": session.get_response_data()
            }
            for session in sessions
        ],
        "total_sessions": len(sessions)
    }
