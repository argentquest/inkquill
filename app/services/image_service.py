# /ai_rag_story_app/app/services/image_service.py

import logging
from typing import Optional

from app.core.config import settings
from .image_providers.base_provider import BaseImageProvider, ImageGenerationResult
from .image_providers.dalle3_provider import Dalle3Provider
from .image_providers.runpod_provider import RunPodProvider

logger = logging.getLogger(__name__)

# A mapping of provider names (from .env) to their implementation classes.
# This makes the service easily extensible.
PROVIDER_MAP = {
    "DALLE3": Dalle3Provider,
    "RUNPOD": RunPodProvider,
}

def get_active_provider() -> Optional[BaseImageProvider]:
    """
    Instantiates and returns the active image generation provider
    based on the application's configuration.
    """
    provider_name = settings.ACTIVE_IMAGE_PROVIDER.upper()
    provider_class = PROVIDER_MAP.get(provider_name)

    if not provider_class:
        logger.error(f"Invalid ACTIVE_IMAGE_PROVIDER configured: '{settings.ACTIVE_IMAGE_PROVIDER}'. Not found in PROVIDER_MAP.")
        return None
    
    try:
        # Create an instance of the chosen provider class
        return provider_class()
    except Exception as e:
        logger.error(f"Failed to instantiate image provider '{provider_name}': {e}", exc_info=True)
        return None


async def generate_image_with_active_provider(
    prompt: str,
    user_id_for_log: int,
    size: str = None
) -> Optional[ImageGenerationResult]:
    """
    The main service function that the rest of the application will call.
    It gets the currently active provider and uses it to generate an image.

    Args:
        prompt: The text prompt for the image.
        user_id_for_log: The ID of the user initiating the request.

    Returns:
        An ImageGenerationResult object or None if generation fails at any step.
    """
    logger.info(f"ImageService: Request received to generate image with active provider '{settings.ACTIVE_IMAGE_PROVIDER}'.")
    
    provider = get_active_provider()
    
    if not provider:
        logger.error("ImageService: Cannot generate image because no active provider could be initialized.")
        return None

    # Use the provided size or default from settings
    image_size = size or settings.DEFAULT_IMAGE_SIZE

    return await provider.generate_image(
        prompt=prompt,
        user_id_for_log=user_id_for_log,
        size=image_size
    )