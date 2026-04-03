"""Service helpers for cost tracker service."""

# /story_app/app/services/cost_tracker_service.py

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
import tiktoken

# --- FIX: Import the new model configuration class ---
from app.models.ai_model_config import AIModelConfiguration, AIProviderEnum

from app.crud import ai_cost_log as crud_ai_cost
from app.schemas.ai_cost_log import AICallLogCreate
from app.db.database import async_session_local
from semantic_kernel.functions.function_result import FunctionResult
from app.services.billing_service import billing_service

logger = logging.getLogger(__name__)

def get_openrouter_token_encoding(model_name: str) -> str:
    """
    Get appropriate tiktoken encoding for OpenRouter models.
    
    Args:
        model_name: The OpenRouter model name (e.g., "anthropic/claude-3.5-sonnet")
        
    Returns:
        The tiktoken encoding name to use
    """
    model_lower = model_name.lower()
    
    # Map OpenRouter model patterns to encodings
    if "claude" in model_lower:
        return "cl100k_base"  # Claude models use similar tokenization
    elif "gpt-4o" in model_lower:
        return "o200k_base"
    elif "gpt-4" in model_lower:
        return "cl100k_base"
    elif "gpt-3.5" in model_lower:
        return "cl100k_base"
    elif "llama" in model_lower:
        return "cl100k_base"  # Approximation for Llama models
    elif "mixtral" in model_lower or "mistral" in model_lower:
        return "cl100k_base"  # Approximation for Mistral models
    elif "qwen" in model_lower:
        return "cl100k_base"  # Approximation for Qwen models
    elif "deepseek" in model_lower:
        return "cl100k_base"  # Approximation for DeepSeek models
    else:
        logger.info(f"Unknown OpenRouter model pattern '{model_name}', using cl100k_base encoding")
        return "cl100k_base"

def calculate_openrouter_cost(usage_data: dict, model_config: AIModelConfiguration) -> float:
    """
    Calculate cost for OpenRouter models.
    
    OpenRouter may provide cost directly in their response, but we still need to map
    to our token-based pricing system for consistency.
    
    Args:
        usage_data: Usage data from OpenRouter API response
        model_config: Model configuration with pricing info
        
    Returns:
        Total cost in USD
    """
    # Check if OpenRouter provided cost directly
    if "cost_usd" in usage_data:
        return float(usage_data["cost_usd"])
    
    # Fall back to token-based calculation using our configured pricing
    input_tokens = usage_data.get("prompt_tokens", 0)
    output_tokens = usage_data.get("completion_tokens", 0)
    
    input_cost = (input_tokens / 1_000_000) * model_config.user_price_input_usd_pm
    output_cost = (output_tokens / 1_000_000) * model_config.user_price_output_usd_pm
    
    return input_cost + output_cost

def estimate_tokens_for_streaming_call(input_text: str, output_text: str, model_name: str) -> Dict[str, int]:
    """
    Estimates token counts for streaming calls using tiktoken.
    Returns a usage dictionary similar to what OpenAI API would return.
    """
    try:
        # Map common model names to tiktoken encodings
        encoding_map = {
            "gpt-4": "cl100k_base",
            "gpt-4o": "o200k_base", 
            "gpt-4o-mini": "o200k_base",
            "gpt-3.5-turbo": "cl100k_base",
            "text-embedding-ada-002": "cl100k_base",
            "text-embedding-3-small": "cl100k_base",
            "text-embedding-3-large": "cl100k_base"
        }
        
        # Default to cl100k_base for unknown models
        encoding_name = encoding_map.get(model_name.lower(), "cl100k_base")
        
        # Handle provider-specific model naming variations
        for key in encoding_map.keys():
            if key in model_name.lower():
                encoding_name = encoding_map[key]
                break
        
        encoding = tiktoken.get_encoding(encoding_name)
        
        # Count tokens
        prompt_tokens = len(encoding.encode(input_text or ""))
        completion_tokens = len(encoding.encode(output_text or ""))
        total_tokens = prompt_tokens + completion_tokens
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    
    except Exception as e:
        logger.warning(f"Failed to estimate tokens for model {model_name}: {e}")
        # Return conservative estimates if tiktoken fails
        input_chars = len(input_text or "")
        output_chars = len(output_text or "")
        # Rough estimate: 1 token ≈ 4 characters for English text
        prompt_tokens = max(1, input_chars // 4)
        completion_tokens = max(1, output_chars // 4)
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

# --- FIX: _calculate_cost now takes the config object ---
def _calculate_cost(model_config: AIModelConfiguration, usage_dict: Dict[str, int]) -> float:
    """Calculates the cost of an AI call based on the model's user pricing."""
    if not model_config:
        logger.warning("No model configuration provided to _calculate_cost. Cost logged as 0.")
        return 0.0

    # Handle provider-specific cost calculation
    if model_config.provider == AIProviderEnum.OPENROUTER:
        return calculate_openrouter_cost(usage_dict, model_config)
    elif model_config.provider == AIProviderEnum.RUNPOD:
        # RunPod uses standard token-based calculation (1 completion token per image)
        prompt_cost = (usage_dict.get("prompt_tokens", 0) / 1_000_000) * model_config.user_price_input_usd_pm
        completion_cost = (usage_dict.get("completion_tokens", 0) / 1_000_000) * model_config.user_price_output_usd_pm
        return prompt_cost + completion_cost
    else:
        # Use standard token-based calculation for OpenAI-compatible models
        prompt_cost = (usage_dict.get("prompt_tokens", 0) / 1_000_000) * model_config.user_price_input_usd_pm
        completion_cost = (usage_dict.get("completion_tokens", 0) / 1_000_000) * model_config.user_price_output_usd_pm
        return prompt_cost + completion_cost

def get_usage_from_sk_result(sk_result: FunctionResult) -> Optional[Dict[str, int]]:
    """Extract usage data from Semantic Kernel result with detailed logging"""
    logger.info(f"Attempting to extract usage from SK result. Result exists: {sk_result is not None}")
    
    if not sk_result:
        logger.warning("SK result is None")
        return None
        
    logger.info(f"SK result metadata exists: {sk_result.metadata is not None}")
    if not sk_result.metadata:
        logger.warning("SK result metadata is None")
        return None
        
    logger.info(f"SK result metadata keys: {list(sk_result.metadata.keys()) if sk_result.metadata else 'No metadata'}")
    
    try:
        usage_data = sk_result.metadata.get('usage')
        logger.info(f"Usage data from metadata: {usage_data}")
        logger.info(f"Usage data type: {type(usage_data)}")
        
        if usage_data:
            logger.info(f"Usage data attributes: {dir(usage_data) if hasattr(usage_data, '__dict__') else 'Not an object'}")
            
            # Try different ways to access usage data
            if hasattr(usage_data, 'prompt_tokens') and hasattr(usage_data, 'completion_tokens'):
                result = {
                    "prompt_tokens": usage_data.prompt_tokens,
                    "completion_tokens": usage_data.completion_tokens,
                    "total_tokens": getattr(usage_data, 'total_tokens', usage_data.prompt_tokens + usage_data.completion_tokens)
                }
                logger.info(f"Successfully extracted usage data: {result}")
                return result
            elif isinstance(usage_data, dict):
                # Try dict access
                if 'prompt_tokens' in usage_data and 'completion_tokens' in usage_data:
                    result = {
                        "prompt_tokens": usage_data['prompt_tokens'],
                        "completion_tokens": usage_data['completion_tokens'],
                        "total_tokens": usage_data.get('total_tokens', usage_data['prompt_tokens'] + usage_data['completion_tokens'])
                    }
                    logger.info(f"Successfully extracted usage data from dict: {result}")
                    return result
                else:
                    logger.warning(f"Usage data dict missing required keys. Available keys: {list(usage_data.keys())}")
            else:
                logger.warning(f"Usage data is not in expected format. Type: {type(usage_data)}, Value: {usage_data}")
        else:
            logger.warning("No usage data found in metadata")
            
        # Check if usage data is stored elsewhere in metadata
        for key, value in sk_result.metadata.items():
            logger.info(f"Metadata key '{key}': {value} (type: {type(value)})")
            
    except Exception as e:
        logger.error(f"Exception while extracting usage data: {e}", exc_info=True)
        return None
        
    logger.warning("No usage data could be extracted from SK result")
    return None

def _get_tokenizer_for_model(model_name: str) -> tiktoken.Encoding:
    """
    Gets the appropriate tiktoken tokenizer for the given model.
    Tries model-specific encoding first, handles OpenRouter models, falls back to cl100k_base.
    """
    try:
        # For OpenRouter models, use the appropriate encoding based on model family
        if "/" in model_name:  # OpenRouter model format like "anthropic/claude-3.5-sonnet"
            encoding_name = get_openrouter_token_encoding(model_name)
            return tiktoken.get_encoding(encoding_name)
        else:
            # Try direct model lookup for OpenAI-compatible models
            return tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to cl100k_base for unknown models
        logger.info(f"Model '{model_name}' not found in tiktoken, using cl100k_base encoding as fallback.")
        return tiktoken.get_encoding("cl100k_base")

def estimate_tokens_for_streaming_call(
    input_text: str, 
    output_text: str, 
    model_name: str
) -> Dict[str, int]:
    """
    Estimates token usage for streaming calls using tiktoken.
    
    Args:
        input_text: The full input prompt/context sent to the model
        output_text: The accumulated output text from the streaming response
        model_name: The model name to determine appropriate tokenizer
        
    Returns:
        Dict with estimated prompt_tokens, completion_tokens, and total_tokens
    """
    try:
        tokenizer = _get_tokenizer_for_model(model_name)
        
        prompt_tokens = len(tokenizer.encode(input_text)) if input_text else 0
        completion_tokens = len(tokenizer.encode(output_text)) if output_text else 0
        total_tokens = prompt_tokens + completion_tokens
        
        logger.info(f"Estimated tokens for streaming call - Input: {prompt_tokens}, Output: {completion_tokens}, Total: {total_tokens}")
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    except Exception as e:
        logger.error(f"Error estimating tokens for model '{model_name}': {e}", exc_info=True)
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

def build_full_prompt_from_kernel_args(kernel_args: "KernelArguments") -> str:
    """
    Attempts to reconstruct the full prompt that would be sent to the model
    from KernelArguments for more accurate token estimation.
    
    Args:
        kernel_args: The KernelArguments object passed to invoke_stream
        
    Returns:
        A string approximating the full prompt sent to the model
    """
    try:
        # Extract common prompt variables that are typically used
        prompt_parts = []
        
        # Add user instruction if available
        user_instruction = getattr(kernel_args, 'user_instruction', None) or \
                          getattr(kernel_args, 'user_instruction_for_scene', None)
        if user_instruction:
            prompt_parts.append(f"User Instruction: {user_instruction}")
        
        # Add context information
        for key in dir(kernel_args):
            if not key.startswith('_') and key not in ['settings']:
                value = getattr(kernel_args, key, None)
                if value and isinstance(value, str) and len(value) > 10:  # Skip short/empty values
                    prompt_parts.append(f"{key}: {value}")
        
        return "\n".join(prompt_parts)
    except Exception as e:
        logger.warning(f"Could not build full prompt from kernel args: {e}")
        return ""

# --- FIX: log_ai_call now takes model_config and input_prompt ---
async def log_ai_call(
    user_id: int,
    model_config: AIModelConfiguration,
    usage: Optional[Dict[str, int]],
    call_type: str,
    input_prompt: Optional[str] = None,
    duration_ms: Optional[int] = None,
    job_id: Optional[str] = None,
    object_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Optional[int]:
    """Logs an AI call. Uses provided db session or creates its own independent transaction."""
    
    # Use provided session or create new one
    if db is not None:
        # Use existing session (no transaction management)
        return await _log_ai_call_internal(db, user_id, model_config, usage, call_type, input_prompt, duration_ms, job_id, object_id)
    else:
        # Create new session with transaction
        async with async_session_local() as new_db:
            return await _log_ai_call_internal(new_db, user_id, model_config, usage, call_type, input_prompt, duration_ms, job_id, object_id)

async def _log_ai_call_internal(
    db: AsyncSession,
    user_id: int,
    model_config: AIModelConfiguration,
    usage: Optional[Dict[str, int]],
    call_type: str,
    input_prompt: Optional[str] = None,
    duration_ms: Optional[int] = None,
    job_id: Optional[str] = None,
    object_id: Optional[int] = None
) -> Optional[int]:
    """Internal function that does the actual logging work."""
    try:
        if usage:
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens
            
            usage_with_total = usage.copy()
            usage_with_total["total_tokens"] = total_tokens
            cost = _calculate_cost(model_config, usage_with_total)
            
            # Check if this looks like estimated usage (total_tokens is exactly prompt + completion)
            if usage.get("total_tokens") == total_tokens and prompt_tokens > 0:
                logger.info(f"Logging AI call for '{call_type}' with estimated usage data (tiktoken-based): {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total tokens")
            else:
                logger.info(f"Logging AI call for '{call_type}' with actual usage data: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total tokens")
        else:
            # Log streaming calls without usage data
            logger.info(f"Logging AI call for '{call_type}' without usage data (streaming call).")
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            cost = 0.0
        
        log_entry = AICallLogCreate(
            job_id=job_id,
            user_id=user_id,
            model_config_id=model_config.id,
            input_prompt=input_prompt,
            model_name=model_config.model_name,
            call_type=call_type,
            object_id=object_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            calculated_cost_usd=cost,
            duration_ms=duration_ms
        )
        created_log = await crud_ai_cost.create_ai_call_log(db, log_in=log_entry)
        
        # Deduct Coins from user account after logging the AI call
        try:
            await billing_service.deduct_ai_cost(
                db=db,
                user_id=user_id,
                model_name=model_config.model_name,
                ai_cost_log_id=created_log.id
            )
        except Exception as billing_error:
            logger.error(f"Failed to deduct Coins for AI call {created_log.id}: {billing_error}")
            # Continue even if billing fails - we don't want to block AI operations
        
        # Capture the ID before any potential session issues
        log_id = created_log.id
        return log_id
    except Exception as e:
        logger.error(f"CRITICAL: Failed to log AI call cost for user {user_id}. Error: {e}", exc_info=True)
        return None

async def log_ai_streaming_call(
    user_id: int,
    model_config: AIModelConfiguration,
    input_prompt: str,
    output_text: str,
    call_type: str,
    duration_ms: Optional[int] = None,
    job_id: Optional[str] = None,
    object_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Optional[int]:
    """
    Logs a streaming AI call using tiktoken to estimate token usage.
    Use this for streaming calls where API doesn't provide usage data.
    Returns the log ID if successful.
    """
    try:
        estimated_usage = estimate_tokens_for_streaming_call(
            input_text=input_prompt,
            output_text=output_text,
            model_name=model_config.model_name
        )

        return await log_ai_call(
            user_id=user_id,
            model_config=model_config,
            usage=estimated_usage,
            call_type=call_type,
            input_prompt=input_prompt,
            duration_ms=duration_ms,
            job_id=job_id,
            object_id=object_id,
            db=db,
        )
    except Exception as e:
        logger.error(f"Error in log_ai_streaming_call: {e}", exc_info=True)
        return None


