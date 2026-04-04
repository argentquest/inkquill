import random
import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class MemoryLanePhotoProvider(BaseCareCircleProvider):
    is_safe_for_patient = False

    """
    Shows a vintage-style photo with a warm description.
    Uses free image APIs for nostalgic photography.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a vintage photo with description.
        
        Returns:
            dict with photo data
        """
        cfg = self.patient_config
        
        # Fallback vintage photos (free, no API key needed)
        fallback_photos = cfg.get("fallback_photos", [
            {
                "image_url": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=600",
                "description": "A lovely lady with a warm smile, dressed in her Sunday best."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600",
                "description": "A kind face full of happy memories and gentle wisdom."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=600",
                "description": "Someone who loved to spend time in the garden."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600",
                "description": "A friendly gentleman with twinkling eyes."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=600",
                "description": "A beautiful lady laughing at a happy memory."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600",
                "description": "A distinguished gentleman with a kind heart."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1542206395-9feb3edaa68d?w=600",
                "description": "Someone who loved the simple things in life."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=600",
                "description": "A man who enjoyed his favorite armchair by the window."
            },
        ])
        
        fallback_description = cfg.get(
            "fallback_description",
            "A warm and happy memory from times gone by."
        )
        
        try:
            # Try to get a random vintage photo from Unsplash
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://source.unsplash.com/600x400/?vintage,portrait",
                    follow_redirects=True,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return {
                        "image_url": str(response.url),
                        "description": random.choice(fallback_photos)["description"]
                    }
        except Exception:
            pass
        
        # Fallback to static content
        photo = random.choice(fallback_photos)
        return {
            "image_url": photo["image_url"],
            "description": photo["description"]
        }
