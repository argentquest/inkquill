# /ai_rag_story_app/app/routers/ai_text_transform.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any
import time
import logging
import semantic_kernel as sk
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

from app.core.deps import get_db_session, get_current_active_user, get_current_user
from app.models.user import User
from app.models.prompt import Prompt, PromptTypeEnum
from app.schemas.ai_text_transform import (
    AITextTransformRequest,
    AITextTransformResponse,
    AITextCostEstimateRequest,
    AITextCostEstimateResponse,
    QuickAIOperationsResponse,
    QuickAIOperation,
    AITextTransformError
)
from app.services.sk_kernel_instance import kernel
from app.services.ai_model_cache import model_cache
from app.services.cost_tracker_service import log_ai_call, get_usage_from_sk_result
from app.services.temperature_optimizer import TemperatureOptimizer, TaskType
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai-text",
    tags=["ai-text-transform"]
)

@router.get("/operations", response_model=QuickAIOperationsResponse)
async def get_quick_ai_operations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all available QuickAI operations for the current user"""
    try:
        # Handle anonymous users - provide basic operations
        if current_user is None:
            # Return basic system prompts for anonymous users
            query = select(Prompt).where(
                and_(
                    Prompt.prompt_type == PromptTypeEnum.QUICK_AI,
                    Prompt.is_active == True,
                    Prompt.user_id.is_(None)  # System prompts only
                )
            ).order_by(Prompt.title)
        else:
            # Get user's own QuickAI prompts and system prompts (no owner)
            query = select(Prompt).where(
                and_(
                    Prompt.prompt_type == PromptTypeEnum.QUICK_AI,
                    Prompt.is_active == True,
                    # Get user's own prompts OR system prompts (no owner)
                    (Prompt.user_id == current_user.id) | (Prompt.user_id.is_(None))
                )
            ).order_by(Prompt.title)
        
        result = await db.execute(query)
        prompts = result.scalars().all()
        
        operations = []
        for prompt in prompts:
            # Map common operations to FontAwesome icons
            icon = _get_icon_for_operation(prompt.title)
            
            operations.append(QuickAIOperation(
                id=prompt.id,
                title=prompt.title,
                description=prompt.reason_to_use,
                icon=icon,
                is_active=prompt.is_active,
                created_at=prompt.created_at
            ))
        
        return QuickAIOperationsResponse(
            operations=operations,
            total_count=len(operations)
        )
        
    except Exception as e:
        logger.error(f"Error fetching QuickAI operations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available operations"
        )

@router.post("/estimate-cost", response_model=AITextCostEstimateResponse)
async def estimate_transformation_cost(
    request: AITextCostEstimateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Estimate the cost of a text transformation operation"""
    try:
        # Handle anonymous users - they can only access system prompts
        if current_user is None:
            query = select(Prompt).where(
                and_(
                    Prompt.id == request.operation_id,
                    Prompt.prompt_type == PromptTypeEnum.QUICK_AI,
                    Prompt.is_active == True,
                    Prompt.user_id.is_(None)  # System prompts only
                )
            )
        else:
            # Get the operation prompt
            query = select(Prompt).where(
                and_(
                    Prompt.id == request.operation_id,
                    Prompt.prompt_type == PromptTypeEnum.QUICK_AI,
                    Prompt.is_active == True,
                    # User can access their own prompts or system prompts (no owner)
                    (Prompt.user_id == current_user.id) | (Prompt.user_id.is_(None))
                )
            )
        
        result = await db.execute(query)
        operation = result.scalar_one_or_none()
        
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found or not accessible"
            )
        
        # Estimate tokens - rough calculation
        # Input text + prompt template + some overhead
        prompt_tokens = len(operation.prompt_content.split()) * 1.3  # Rough token estimate
        text_tokens = len(request.text.split()) * 1.3
        estimated_tokens = int(prompt_tokens + text_tokens + 50)  # Add overhead
        
        # Get current AI model pricing
        model_config = model_cache.default_generation_model
        if not model_config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No AI model available"
            )
        
        # Rough cost estimation (this would need to be more sophisticated in production)
        cost_per_1k_tokens = 0.002  # Example rate
        estimated_cost = (estimated_tokens / 1000) * cost_per_1k_tokens
        
        return AITextCostEstimateResponse(
            estimated_tokens=estimated_tokens,
            estimated_cost=round(estimated_cost, 4),
            operation_name=operation.title
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estimating cost: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to estimate cost"
        )

@router.post("/transform", response_model=AITextTransformResponse)
async def transform_text(
    request: AITextTransformRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Transform text using AI based on the selected operation"""
    start_time = time.time()
    
    try:
        # Handle anonymous users - they can only access system prompts
        if current_user is None:
            query = select(Prompt).where(
                and_(
                    Prompt.id == request.operation_id,
                    Prompt.prompt_type == PromptTypeEnum.QUICK_AI,
                    Prompt.is_active == True,
                    Prompt.user_id.is_(None)  # System prompts only
                )
            )
        else:
            # Get the operation prompt
            query = select(Prompt).where(
                and_(
                    Prompt.id == request.operation_id,
                    Prompt.prompt_type == PromptTypeEnum.QUICK_AI,
                    Prompt.is_active == True,
                    # User can access their own prompts or system prompts (no owner)
                    (Prompt.user_id == current_user.id) | (Prompt.user_id.is_(None))
                )
            )
        
        result = await db.execute(query)
        operation = result.scalar_one_or_none()
        
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found or not accessible"
            )
        
        # Prepare the prompt with context
        prompt_content = operation.prompt_content
        
        # Replace placeholders in the prompt
        prompt_content = prompt_content.replace("{text}", request.text)
        
        # Add context if available
        if request.context:
            context_str = _format_context(request.context)
            prompt_content = prompt_content.replace("{context_summary}", context_str)
        else:
            # Remove the context placeholder if no context is provided
            prompt_content = prompt_content.replace("{context_summary}", "No additional context provided")
        
        # Get AI model configuration
        model_config = model_cache.default_generation_model
        if not model_config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No AI model available for text transformation"
            )
        
        # Optimize temperature for text transformation task
        temperature, explanation = TemperatureOptimizer().get_optimal_temperature(
            model_name=model_config.model_name,
            task_type=TaskType.EDITING
        )
        
        # Create execution settings
        execution_settings = AzureChatPromptExecutionSettings(
            service_id="azure_openai_chat_service",
            temperature=temperature,
            max_tokens=model_config.max_tokens,
            top_p=model_config.top_p
        )
        
        # Execute the transformation directly using the kernel
        result = await kernel.invoke_prompt(
            prompt=prompt_content,
            kernel_arguments=KernelArguments(settings=execution_settings)
        )
        
        if not result or not result.value:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI transformation failed to produce output"
            )
        
        # Extract content from result - handle different response formats
        transformed_text = None
        
        try:
            # Try to extract from ChatMessageContent
            if hasattr(result.value, 'inner_content'):
                inner = result.value.inner_content
                if hasattr(inner, 'choices') and len(inner.choices) > 0:
                    transformed_text = inner.choices[0].message.content
                elif hasattr(inner, 'content'):
                    transformed_text = inner.content
            
            # Try to extract from direct message content
            if not transformed_text and hasattr(result.value, 'content'):
                transformed_text = result.value.content
                
            # Try to extract from list of messages
            if not transformed_text and isinstance(result.value, list) and len(result.value) > 0:
                first_item = result.value[0]
                if hasattr(first_item, 'content'):
                    transformed_text = first_item.content
                elif hasattr(first_item, 'inner_content') and hasattr(first_item.inner_content, 'choices'):
                    transformed_text = first_item.inner_content.choices[0].message.content
            
            # Fallback to string conversion
            if not transformed_text:
                transformed_text = str(result.value)
                
        except Exception as e:
            logger.warning(f"Error extracting content from result: {e}")
            transformed_text = str(result.value)
        
        # Clean up the text if it still contains object representations
        if transformed_text and 'ChatMessageContent' in transformed_text:
            # Try to extract just the content part from the string representation
            import re
            content_match = re.search(r"content='([^']*)'", transformed_text)
            if content_match:
                transformed_text = content_match.group(1)
            else:
                # If regex fails, try to find content between quotes
                start_quote = transformed_text.find("content='")
                if start_quote != -1:
                    start_quote += 9  # len("content='")
                    end_quote = transformed_text.find("'", start_quote)
                    if end_quote != -1:
                        transformed_text = transformed_text[start_quote:end_quote]
        
        transformed_text = transformed_text.strip() if transformed_text else ""
        
        # Don't convert to HTML - let Quill handle the formatting
        # Just clean up any escaped characters that might be in the response
        transformed_text = transformed_text.replace('\\n', '\n')
        transformed_text = transformed_text.replace('\\"', '"')
        transformed_text = transformed_text.replace("\\'", "'")
        
        # Remove any markdown formatting that might interfere
        transformed_text = transformed_text.replace('**', '')  # Remove bold markers
        transformed_text = transformed_text.replace('*', '')   # Remove italic markers
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Get usage information from result
        usage = get_usage_from_sk_result(result) or {}
        
        # If no usage data from semantic kernel, estimate using tiktoken
        if not usage or usage.get('total_tokens', 0) == 0:
            logger.info("No usage data from semantic kernel, estimating tokens using tiktoken")
            from app.services.cost_tracker_service import estimate_tokens_for_streaming_call
            usage = estimate_tokens_for_streaming_call(
                input_text=prompt_content,
                output_text=transformed_text,
                model_name=model_config.model_name
            )
        
        # Calculate cost using model configuration
        from app.services.cost_tracker_service import _calculate_cost
        tokens_used = usage.get('total_tokens', 0)
        cost_estimate = _calculate_cost(model_config, usage)
        
        # Log the AI call for cost tracking (skip for anonymous users)
        if current_user is not None:
            await log_ai_call(
                user_id=current_user.id,
                model_config=model_config,
                usage=usage,
                call_type='text_transformation',
                input_prompt=prompt_content[:500] if prompt_content else None,  # Truncate for logging
                duration_ms=int(processing_time * 1000),
                db=db
            )
        
        return AITextTransformResponse(
            success=True,
            transformed_text=transformed_text,
            original_text=request.text,
            operation_used=operation.title,
            tokens_used=tokens_used,
            cost_estimate=cost_estimate,
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transforming text: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text transformation failed: {str(e)}"
        )

def _get_icon_for_operation(title: str) -> str:
    """Map operation titles to FontAwesome icons"""
    title_lower = title.lower()
    
    if 'rewrite' in title_lower or 'rephrase' in title_lower:
        return "fas fa-edit"
    elif 'expand' in title_lower or 'elaborate' in title_lower:
        return "fas fa-expand-arrows-alt"
    elif 'simplify' in title_lower or 'simple' in title_lower:
        return "fas fa-compress"
    elif 'formal' in title_lower:
        return "fas fa-user-tie"
    elif 'casual' in title_lower:
        return "fas fa-smile"
    elif 'grammar' in title_lower or 'correct' in title_lower:
        return "fas fa-spell-check"
    elif 'emotion' in title_lower or 'feel' in title_lower:
        return "fas fa-heart"
    elif 'action' in title_lower or 'dynamic' in title_lower:
        return "fas fa-bolt"
    elif 'dialogue' in title_lower or 'conversation' in title_lower:
        return "fas fa-comments"
    elif 'description' in title_lower or 'describe' in title_lower:
        return "fas fa-eye"
    else:
        return "fas fa-magic"

def _format_context(context: Dict[str, Any]) -> str:
    """Format context information for the AI prompt"""
    if not context:
        return ""
    
    context_parts = []
    
    # Handle context_summary if provided (preferred method)
    if context.get('context_summary'):
        context_parts.append(context['context_summary'])
    
    # Handle different editor types
    editor_type = context.get('type', 'unknown')
    
    if editor_type == 'basic_story':
        if context.get('story_title'):
            context_parts.append(f"Story: {context['story_title']}")
        if context.get('word_count'):
            context_parts.append(f"Word count: {context['word_count']} words")
            
    elif editor_type == 'scene':
        if context.get('story_title'):
            context_parts.append(f"Story: {context['story_title']}")
        if context.get('act_title'):
            context_parts.append(f"Act: {context['act_title']}")
        if context.get('scene_title'):
            context_parts.append(f"Scene: {context['scene_title']}")
        if context.get('word_count'):
            context_parts.append(f"Word count: {context['word_count']} words")
            
    elif editor_type == 'act':
        if context.get('story_title'):
            context_parts.append(f"Story: {context['story_title']}")
        if context.get('act_title'):
            context_parts.append(f"Act: {context['act_title']}")
        if context.get('word_count'):
            context_parts.append(f"Word count: {context['word_count']} words")
    
    # Add excerpt if available
    if context.get('story_excerpt'):
        context_parts.append(f"Story excerpt: {context['story_excerpt']}")
    
    return "\n".join(context_parts) if context_parts else ""