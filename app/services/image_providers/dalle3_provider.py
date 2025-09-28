# /ai_rag_story_app/app/services/image_providers/dalle3_provider.py

import logging
import base64
import time
from typing import Optional

# Using AsyncOpenAI is correct if you are using the standard API key (sk-...)
# and not an Azure-specific endpoint for DALL-E. Let's stick with this since it worked before.
from openai import AsyncOpenAI
from app.core.config import settings
from .base_provider import BaseImageProvider, ImageGenerationResult
from app.services.cost_tracker_service import log_ai_call
from app.services.ai_model_cache import model_cache

logger = logging.getLogger(__name__)

class Dalle3Provider(BaseImageProvider):
    """
    An image generation provider that uses the standard OpenAI DALL-E 3 service.
    """

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("DALL-E 3 provider is not configured. Missing OPENAI_API_KEY.")
        
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Dalle3Provider initialized for standard OpenAI API.")

    async def generate_image(
        self,
        prompt: str,
        user_id_for_log: int,
        size: str = "1024x1024"
    ) -> Optional[ImageGenerationResult]:
        
        # --- FIX: ADD DETAILED LOGGING OF THE FINAL PROMPT ---
        logger.info(f"Dalle3Provider: Preparing to generate image for user {user_id_for_log}.")
        logger.info(f"Dalle3Provider: FINAL PROMPT being sent to OpenAI: >>> {prompt} <<<")
        # --- END FIX ---
        
        start_time = time.perf_counter()

        try:
            result = await self.client.images.generate(
                model=settings.OPENAI_DALLE3_MODEL,
                prompt=prompt,
                n=1,
                size=size,
                quality="hd",
                style="vivid",
                response_format="b64_json"
            )
            
            end_time = time.perf_counter()
            duration_ms = int((end_time - start_time) * 1000)

            if not result.data or not result.data[0].b64_json:
                raise ValueError("DALL-E 3 API response did not contain base64 image data.")

            # Try to log AI cost if model configuration exists
            try:
                # Find model configuration for DALL-E 3
                dalle_model_config = None
                for config in model_cache.configurations.values():
                    if config.model_name == settings.OPENAI_DALLE3_MODEL:
                        dalle_model_config = config
                        break
                
                if dalle_model_config:
                    usage_dict = {
                        "prompt_tokens": 0,
                        "completion_tokens": 1,
                        "total_tokens": 1
                    }
                    await log_ai_call(
                        user_id=user_id_for_log,
                        model_config=dalle_model_config,
                        usage=usage_dict,
                        call_type="image_generation",
                        input_prompt=prompt,
                        duration_ms=duration_ms
                    )
                    logger.info(f"Logged DALL-E 3 cost for user {user_id_for_log}")
                else:
                    logger.warning(f"No model configuration found for DALL-E model '{settings.OPENAI_DALLE3_MODEL}'. Skipping cost logging.")
            except Exception as cost_log_error:
                logger.error(f"Failed to log DALL-E cost, but image generation succeeded: {cost_log_error}")
                # Don't fail the image generation if cost logging fails

            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            content_type = "image/png"

            revised_prompt = result.data[0].revised_prompt or prompt

            logger.info(f"Dalle3Provider: Successfully generated image for user {user_id_for_log}.")
            
            return ImageGenerationResult(
                image_bytes=image_bytes,
                content_type=content_type,
                revised_prompt=revised_prompt
            )

        except Exception as e:
            logger.error(f"Dalle3Provider: Error during image generation: {e}", exc_info=True)
            
            # Log more details for debugging 400 errors
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_details = e.response.json()
                    logger.error(f"Dalle3Provider: API Error Details: {error_details}")
                    if 'error' in error_details and error_details['error'].get('type') == 'image_generation_user_error':
                        logger.error(f"Dalle3Provider: Prompt rejected by OpenAI. Original prompt: '{prompt}'")
                except:
                    pass
                    
            return None