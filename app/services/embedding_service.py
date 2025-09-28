# /ai_rag_story_app/app/services/embedding_service.py

from openai import AsyncAzureOpenAI, types
from openai.types.completion_usage import CompletionUsage # Import is necessary here
import os
import time
from typing import Optional, List
import logging # Import logging

from app.core.config import settings
from app.services.cost_tracker_service import log_ai_call

# Get logger instance
logger = logging.getLogger(__name__)

_shared_embedding_client: Optional[AsyncAzureOpenAI] = None

def initialize_embedding_client():
    global _shared_embedding_client
    if _shared_embedding_client is None:
        if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME:
            try:
                _shared_embedding_client = AsyncAzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    azure_endpoint=str(settings.AZURE_OPENAI_ENDPOINT),
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                )
                logger.info("Shared Azure OpenAI embedding client initialized.") # Use logger
            except Exception as e:
                logger.error(f"Failed to initialize shared Azure OpenAI embedding client: {e}", exc_info=True) # Use logger
        else:
            logger.error("Shared Azure OpenAI embedding configuration is missing.") # Use logger

async def close_embedding_client():
    global _shared_embedding_client
    if _shared_embedding_client:
        try:
            await _shared_embedding_client.close()
            _shared_embedding_client = None
            logger.info("Shared Azure OpenAI embedding client closed.") # Use logger
        except Exception as e:
            logger.error(f"Failed to close shared Azure OpenAI embedding client: {e}", exc_info=True) # Use logger

def get_embedding_client() -> Optional[AsyncAzureOpenAI]:
    if _shared_embedding_client is None:
         logger.warning("Shared embedding client accessed before initialization.") # Use logger
    return _shared_embedding_client

async def generate_embeddings(texts: List[str], user_id: int) -> Optional[List[List[float]]]:
    aclient = get_embedding_client()
    if not aclient or not settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME:
        logger.error("Embedding client or deployment name not available.") # Use logger
        return None

    if not texts:
        return []

    try:
        start_time = time.perf_counter()
        response = await aclient.embeddings.create(
            input=texts,
            model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
        )
        end_time = time.perf_counter()
        duration_ms = int((end_time - start_time) * 1000)

        if response.usage:
            # --- BEGIN SECURITY FIX ---
            # Safely access attributes that may not exist in all response types.
            # Embedding usage objects do not have 'completion_tokens'.
            usage_dict = {
                "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(response.usage, 'completion_tokens', 0), # Will default to 0 for embeddings
            }
            # --- END SECURITY FIX ---
            # TODO: Fix cost logging for embeddings to use new model_config parameter
            logger.info(f"Embedding call completed - tokens: {usage_dict}, duration: {duration_ms}ms")
        
        if response.data and len(response.data) == len(texts):
            return [item.embedding for item in response.data]
        else:
            logger.warning(f"Embedding response data length mismatch or missing data. Expected {len(texts)}, Got {len(response.data) if response.data else 0}")
            return None
    except Exception as e:
        logger.error(f"Failed to generate embeddings. Error: {e}", exc_info=True) # Use logger
        return None