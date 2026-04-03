"""Service helpers for dalle3 provider."""

# /story_app/app/services/image_providers/dalle3_provider.py

import logging
import base64
import time
from typing import Optional

# Using AsyncOpenAI with the standard OpenAI API is the intended path here.
from openai import AsyncOpenAI
from app.core.config import settings
from .base_provider import BaseImageProvider, ImageGenerationResult
from app.services.cost_tracker_service import log_ai_call
from app.services.ai_model_cache import model_cache

logger = logging.getLogger(__name__)

class Dalle3Provider(BaseImageProvider):
    """
    Image generation provider using OpenAI's gpt-image-1 model.
    """

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI image provider is not configured. Missing OPENAI_API_KEY.")

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info(f"Dalle3Provider initialized with model '{settings.OPENAI_IMAGE_MODEL}'.")

    async def generate_image(
        self,
        prompt: str,
        user_id_for_log: int,
        size: str = "1024x1024"
    ) -> Optional[ImageGenerationResult]:

        logger.info(f"Dalle3Provider: Generating image for user {user_id_for_log} with model '{settings.OPENAI_IMAGE_MODEL}'.")
        logger.info(f"Dalle3Provider: Prompt >>> {prompt} <<<")

        start_time = time.perf_counter()

        try:
            result = await self.client.images.generate(
                model=settings.OPENAI_IMAGE_MODEL,
                prompt=prompt,
                n=1,
                size=size,
                quality="high",
                response_format="b64_json"
            )

            end_time = time.perf_counter()
            duration_ms = int((end_time - start_time) * 1000)

            if not result.data or not result.data[0].b64_json:
                raise ValueError("OpenAI image API response did not contain base64 image data.")

            try:
                image_model_config = None
                for config in model_cache.configurations.values():
                    if config.model_name == settings.OPENAI_IMAGE_MODEL:
                        image_model_config = config
                        break

                if image_model_config:
                    usage_dict = {"prompt_tokens": 0, "completion_tokens": 1, "total_tokens": 1}
                    await log_ai_call(
                        user_id=user_id_for_log,
                        model_config=image_model_config,
                        usage=usage_dict,
                        call_type="image_generation",
                        input_prompt=prompt,
                        duration_ms=duration_ms
                    )
                    logger.info(f"Logged image generation cost for user {user_id_for_log}")
                else:
                    logger.warning(f"No model configuration found for '{settings.OPENAI_IMAGE_MODEL}'. Skipping cost logging.")
            except Exception as cost_log_error:
                logger.error(f"Failed to log image generation cost, but image generation succeeded: {cost_log_error}")

            image_bytes = base64.b64decode(result.data[0].b64_json)

            logger.info(f"Dalle3Provider: Successfully generated image for user {user_id_for_log}.")

            return ImageGenerationResult(
                image_bytes=image_bytes,
                content_type="image/png",
                revised_prompt=prompt
            )

        except Exception as e:
            logger.error(f"Dalle3Provider: Error during image generation: {e}", exc_info=True)
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_details = e.response.json()
                    logger.error(f"Dalle3Provider: API Error Details: {error_details}")
                except Exception:
                    pass
            return None

