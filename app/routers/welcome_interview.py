"""API routes for welcome interview."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import json
import logging
import os
from pathlib import Path
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.deps import get_db_session, get_current_active_user
from app.models.user_interview_response import UserInterviewResponse
from app.models.user import User
from app.models.user_transaction import TransactionType
from app.crud import user as crud_user
from app.crud import ai_model_config as ai_model_crud
from app.crud.billing import billing_crud
from app.schemas.billing import UserTransactionCreate
from app.schemas.base import ApiResponse
from app.services.langgraph_runtime_setup import kernel
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result
from app.services.langgraph_kernel import KernelArguments, OpenAIChatPromptExecutionSettings, PromptTemplateConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui/welcome-interview/api", tags=["welcome-interview-api"])


class AnalysisRequest(BaseModel):
    """Response or helper model for analysis request."""
    interview_response_id: int = Field(..., description="ID of the interview response to analyze")


class AnalysisResponse(BaseModel):
    """Response or helper model for analysis response."""
    writer_score: int = Field(..., ge=1, le=10, description="Writer skill level from 1-10")
    recommendations: list[str] = Field(..., description="Personalized recommendations")
    book_suggestions: list[Dict[str, str]] = Field(..., description="Recommended books")
    strengths: list[Dict[str, str]] = Field(..., description="Identified strengths")
    areas_for_improvement: list[Dict[str, str]] = Field(..., description="Areas for improvement")
    genre_analysis: str = Field(..., description="Genre preference analysis")


class BonusRequest(BaseModel):
    """Response or helper model for bonus request."""
    bonus_number: int = Field(..., ge=1, le=10, description="Bonus number (1-10)")


class BonusResponse(BaseModel):
    """Response or helper model for bonus response."""
    success: bool = Field(..., description="Whether the bonus was awarded")
    message: str = Field(..., description="Response message")
    coins_awarded: int = Field(..., description="Number of coins awarded")
    already_claimed: bool = Field(..., description="Whether bonus was already claimed")


@router.post("/analyze", response_model=ApiResponse)
async def analyze_interview(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Analyze interview responses and provide personalized recommendations"""
    
    logger.info(f"Analyzing interview response {request.interview_response_id} for user {current_user.id}")
    
    try:
        # Get the interview response
        result = await db.execute(
            select(UserInterviewResponse).filter(
                UserInterviewResponse.id == request.interview_response_id,
                UserInterviewResponse.user_id == current_user.id
            )
        )
        interview_response = result.scalar_one_or_none()
        
        if not interview_response:
            logger.error(f"Interview response {request.interview_response_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=404,
                detail="Interview response not found"
            )
        
        logger.info(f"Found interview response: ID={interview_response.id}, interview_id={interview_response.interview_id}")
        
    except Exception as e:
        logger.error(f"Error fetching interview response: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error fetching interview response"
        )
    
    # Verify this is the new_user_onboarding interview
    if interview_response.interview_id != "new_user_onboarding":
        logger.error(f"Invalid interview type: {interview_response.interview_id}. Expected: new_user_onboarding")
        raise HTTPException(
            status_code=400,
            detail="This endpoint only analyzes new user onboarding interviews"
        )
    
    try:
        # Format the interview responses for the AI
        logger.info("Starting to format interview responses...")
        response_data = interview_response.get_response_data()
        logger.info(f"Response data keys: {list(response_data.keys())}")
        
        # Extract responses in a readable format
        responses = response_data.get("responses", {})
        logger.info(f"Found {len(responses)} responses: {list(responses.keys())}")
        formatted_responses = []
        
        # Format each question and response
        for question_id, answer_data in responses.items():
            logger.debug(f"Processing question {question_id}: {answer_data}")
            
            # Extract selected values from the answer data structure
            if isinstance(answer_data, dict) and "selected_values" in answer_data:
                selected_values = answer_data["selected_values"]
                if isinstance(selected_values, list):
                    answer_text = ", ".join(selected_values)
                else:
                    answer_text = str(selected_values)
            else:
                # Fallback for different data structures
                answer_text = str(answer_data)
            
            if question_id == "writing_experience":
                formatted_responses.append(f"Writing Experience: {answer_text}")
            elif question_id == "genre_preferences":
                formatted_responses.append(f"Preferred Genres: {answer_text}")
            elif question_id == "help_needed":
                formatted_responses.append(f"Areas Seeking Help: {answer_text}")
            elif question_id == "writing_stage":
                formatted_responses.append(f"Current Writing Stage: {answer_text}")
            elif question_id == "next_step":
                formatted_responses.append(f"Preferred Starting Point: {answer_text}")
            elif question_id == "brainstorming_popup":
                formatted_responses.append(f"Interest in Brainstorming: {answer_text}")
        
        interview_text = "\n".join(formatted_responses)
        
        logger.info(f"Formatted interview responses for AI analysis")
        logger.info(f"Formatted interview text: {interview_text}")
        
        # Load the prompt file
        prompts_dir = Path(__file__).parent.parent / "prompts" / "system"
        prompt_file = prompts_dir / "welcome_interview_analysis.txt"
        
        logger.info(f"Looking for prompt file at: {prompt_file}")
        
        if not prompt_file.exists():
            logger.error(f"Welcome interview prompt file not found: {prompt_file}")
            raise HTTPException(
                status_code=500,
                detail="Welcome interview analysis prompt not found"
            )
        
        # Load the prompt content
        logger.info("Loading prompt content...")
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        logger.info(f"Prompt content loaded, length: {len(prompt_content)}")
        
        # Replace the variable in the prompt
        formatted_prompt = prompt_content.replace("{{interview_responses}}", interview_text)
        logger.info("Prompt variables replaced")
        
        # Get AI model settings (same as Gallery Chat)
        logger.info("Getting AI model configuration...")
        ai_model_config = await ai_model_crud.get_default_model_config(db)
        if not ai_model_config:
            logger.error("No default AI model configuration found")
            raise HTTPException(
                status_code=500,
                detail="AI model configuration not available"
            )
        
        logger.info(f"Using model: {ai_model_config.model_name}")
        
        # Create prompt execution settings
        logger.info("Creating execution settings...")
        execution_settings = OpenAIChatPromptExecutionSettings(
            service_id="chat_service",
            max_tokens=2000,
            temperature=0.3
            # Note: Removed response_format to avoid the validation error
        )
        
        # Create and execute the prompt
        logger.info("Creating prompt template config...")
        prompt_config = PromptTemplateConfig(
            template=formatted_prompt,
            name="WelcomeInterviewAnalysis",
            template_format="semantic-kernel",
            description="Analyze welcome interview responses",
            input_variables=[
                {
                    "name": "interview_responses",
                    "description": "Complete interview responses from the user",
                    "is_required": True
                }
            ],
            execution_settings={"chat_service": execution_settings}
        )
        
        # Create the function and invoke it
        logger.info("Adding function to kernel...")
        welcome_function = kernel.add_function(
            function_name="AnalyzeWelcomeInterview",
            plugin_name="WelcomeInterview",
            prompt_template_config=prompt_config
        )
        
        logger.info("Invoking AI function...")
        # Pass the interview responses as an argument
        arguments = KernelArguments(interview_responses=interview_text)
        result = await welcome_function.invoke(kernel, arguments)
        ai_result = str(result)
        logger.info(f"AI result received, length: {len(ai_result)}")
        
        # Log AI cost tracking and automatically deduct from user account
        try:
            # First try to extract usage data from the storytelling runtime result
            usage_data = get_usage_from_sk_result(result)
            logger.info(f"Usage data from SK result: {usage_data}")
            
            # If no usage data found or zero values, estimate it manually
            if not usage_data or usage_data.get("total_tokens", 0) == 0:
                logger.warning(f"No valid usage data found in SK result (provider: {ai_model_config.provider}), estimating token usage manually")
                from app.services.cost_tracker_service import estimate_tokens_for_streaming_call
                
                # Estimate tokens for input (prompt + interview responses)
                input_text = formatted_prompt + "\n" + interview_text
                output_text = ai_result
                
                usage_data = estimate_tokens_for_streaming_call(
                    input_text=input_text,
                    output_text=output_text,
                    model_name=ai_model_config.model_name
                )
                logger.info(f"Estimated token usage for {ai_model_config.provider} provider: {usage_data}")
            else:
                logger.info(f"Using actual usage data from {ai_model_config.provider} provider: {usage_data}")
            
            # Ensure we have valid usage data before logging
            if usage_data and usage_data.get("total_tokens", 0) > 0:
                await log_ai_call(
                    user_id=current_user.id,
                    model_config=ai_model_config,
                    usage=usage_data,
                    call_type="welcome_interview_analysis",
                    input_prompt=interview_text[:500] + "..." if len(interview_text) > 500 else interview_text,
                    db=db
                )
                logger.info(f"AI cost logged and deducted for welcome interview analysis: {usage_data.get('total_tokens', 0)} tokens")
            else:
                logger.error("Failed to get valid token usage data, skipping cost logging")
                
        except Exception as e:
            logger.error(f"Failed to log AI cost for welcome interview: {e}", exc_info=True)
        
        logger.info(f"AI analysis completed for user {current_user.id}")
        
        # Parse the AI response (it should be JSON)
        try:
            analysis_result = json.loads(ai_result)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"AI response: {ai_result}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse AI analysis results"
            )
        
        # Validate the AI response structure
        required_fields = ["writer_score", "recommendations", "book_suggestions", 
                          "strengths", "areas_for_improvement", "genre_analysis"]
        for field in required_fields:
            if field not in analysis_result:
                logger.error(f"Missing required field in AI response: {field}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Incomplete AI analysis: missing {field}"
                )
        
        # Update user's interview_data field with the analysis
        current_user.interview_data = {
            "completed_at": interview_response.created_at.isoformat(),
            "analysis": analysis_result,
            "interview_response_id": request.interview_response_id
        }
        
        # Automatically award Step 1 bonus if not already claimed
        logger.info(f"Checking bonus1 status for user {current_user.id}: bonus1={current_user.bonus1}")
        if not current_user.bonus1:
            logger.info(f"Automatically awarding Step 1 bonus to user {current_user.id}")
            
            # Mark Step 1 bonus as claimed
            current_user.bonus1 = True
            logger.info(f"Set bonus1=True for user {current_user.id}")
            
            # Award 500 coins for completing the interview (bonus1)
            coins_to_award = Decimal('500.0000')
            account = await billing_crud.get_or_create_user_account(db, current_user.id)
            new_balance = account.current_balance + coins_to_award
            
            # Create step bonus transaction
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.STEP_BONUS,
                amount=coins_to_award,
                balance_after=new_balance,
                description="Step Bonus: Intro Interview - 500 Coins",
                transaction_metadata={"step_number": 1, "step_name": "Intro Interview", "auto_awarded": True}
            )
            
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and total credits added
            account.current_balance = new_balance
            account.total_credits_added += coins_to_award
            
            logger.info(f"Awarded 500 coins to user {current_user.id} for completing interview")
        
        # Commit the update
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"Successfully analyzed interview and updated user {current_user.id} profile")
        
        return analysis_result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error analyzing interview for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze interview responses"
        )


@router.get("/bonus-status")
async def get_bonus_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get the current bonus status for the user"""
    try:
        bonus_status = {
            "bonus1": current_user.bonus1,  # Step 1: Intro Interview (75 coins)
            "bonus2": current_user.bonus2,  # Step 2: Story Brainstorm (50 coins)
            "bonus3": current_user.bonus3,  # Step 3: Start Writing (50 coins)
            "bonus4": current_user.bonus4,  # Future bonus
            "bonus5": current_user.bonus5,  # Future bonus
            "bonus6": current_user.bonus6,  # Future bonus
            "bonus7": current_user.bonus7,  # Future bonus
            "bonus8": current_user.bonus8,  # Future bonus
            "bonus9": current_user.bonus9,  # Future bonus
            "bonus10": current_user.bonus10, # Future bonus
        }
        
        logger.info(f"Retrieved bonus status for user {current_user.id}: {bonus_status}")
        return ApiResponse.success_response(data=bonus_status)
        
    except Exception as e:
        logger.error(f"Error getting bonus status for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to get bonus status"
        )


@router.post("/claim-bonus", response_model=ApiResponse)
async def claim_bonus(
    request: BonusRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Claim a bonus reward if not already claimed"""
    try:
        bonus_number = request.bonus_number
        
        # Define coin amounts for each bonus (in Coins - 1 Coin = $0.0001)
        bonus_coin_amounts = {
            1: Decimal('500.0000'),   # Step 1: Intro Interview - 500 coins
            2: Decimal('500.0000'),   # Step 2: Story Brainstorm - 500 coins
            3: Decimal('1000.0000'),  # Step 3: Start Writing - 1000 coins
            4: Decimal('0.0000'),     # Future bonus
            5: Decimal('0.0000'),     # Future bonus
            6: Decimal('0.0000'),     # Future bonus
            7: Decimal('0.0000'),     # Future bonus
            8: Decimal('0.0000'),     # Future bonus
            9: Decimal('0.0000'),     # Future bonus
            10: Decimal('0.0000'),    # Future bonus
        }
        
        # Check if bonus exists and get coin amount
        if bonus_number not in bonus_coin_amounts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid bonus number: {bonus_number}"
            )
        
        coins_to_award = bonus_coin_amounts[bonus_number]
        
        # Check if bonus was already claimed
        bonus_attr = f"bonus{bonus_number}"
        already_claimed = getattr(current_user, bonus_attr, False)
        
        if already_claimed:
            logger.info(f"User {current_user.id} attempted to claim bonus {bonus_number} again")
            return ApiResponse.success_response(
                data=BonusResponse(
                    success=False,
                    message=f"Bonus {bonus_number} already claimed",
                    coins_awarded=0,
                    already_claimed=True
                )
            )
        
        # Award the bonus
        setattr(current_user, bonus_attr, True)
        
        # Add actual coins to user's account using the billing system
        if coins_to_award > 0:
            # Get or create user account
            account = await billing_crud.get_or_create_user_account(db, current_user.id)
            
            # Calculate new balance
            new_balance = account.current_balance + coins_to_award
            
            # Create step bonus transaction
            step_names = {
                1: "Intro Interview",
                2: "Story Brainstorm", 
                3: "Start Writing"
            }
            step_name = step_names.get(bonus_number, f"Step {bonus_number}")
            
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.STEP_BONUS,
                amount=coins_to_award,
                balance_after=new_balance,
                description=f"Step Bonus: {step_name} - {coins_to_award} Coins",
                transaction_metadata={"step_number": bonus_number, "step_name": step_name}
            )
            
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and total credits added
            account.current_balance = new_balance
            account.total_credits_added += coins_to_award
        
        # Commit the changes
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"User {current_user.id} claimed bonus {bonus_number} for {coins_to_award} coins")
        
        return ApiResponse.success_response(
            data=BonusResponse(
                success=True,
                message=f"Bonus {bonus_number} claimed successfully!",
                coins_awarded=int(coins_to_award),
                already_claimed=False
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error claiming bonus {request.bonus_number} for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to claim bonus"
        )
