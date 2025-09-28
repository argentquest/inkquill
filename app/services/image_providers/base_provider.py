# /ai_rag_story_app/app/services/image_providers/base_provider.py

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

class ImageGenerationResult(BaseModel):
    """
    A standardized data structure for returning the result of an image generation.
    All providers must return this object.
    """
    image_bytes: bytes
    content_type: str = "image/png"
    revised_prompt: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True # Allows the 'bytes' type

class BaseImageProvider(ABC):
    """
    Abstract Base Class for all image generation providers.
    It defines the common interface that the ImageService will use to interact
    with any configured image generation model (DALL-E 3, RunPod, etc.).
    """

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        user_id_for_log: int,
        size: str = "1024x1024"
    ) -> Optional[ImageGenerationResult]:
        """
        The primary method for generating an image.

        Args:
            prompt: The text prompt to generate the image from.
            user_id_for_log: The ID of the user initiating the call, for any
                             potential logging or tracking.
            size: The desired size of the image, e.g., "1024x1024".

        Returns:
            An ImageGenerationResult object containing the image data and metadata,
            or None if the generation failed.
        """
        pass