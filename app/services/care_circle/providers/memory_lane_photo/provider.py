import random
import httpx
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class MemoryLanePhotoProvider(BaseCareCircleProvider):
    provider_key = "memory_lane_photo"
    is_safe_for_patient = True

    """
    Shows a vintage-style photo with a warm description.
    Uses free image APIs for nostalgic photography.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a vintage photo with description.
        Uses pre-configured vintage photos from Unsplash (no external API call).
        
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
            {
                "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600",
                "description": "A graceful woman enjoying a peaceful afternoon tea."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&sat=-100",
                "description": "A thoughtful gentleman reading by the fireside."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=600",
                "description": "A warm smile from someone who has lived a full and happy life."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=600",
                "description": "A couple enjoying a gentle walk together in the park."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1516733725897-1aa73b87c8e8?w=600",
                "description": "Someone tending to beautiful flowers in a sunny garden."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e01e5?w=600",
                "description": "A kind soul who always had time for a friendly chat."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1548142813-c348350df52b?w=600",
                "description": "A family gathering filled with laughter and love."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=600",
                "description": "A young woman remembering happy days gone by."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=600",
                "description": "A proud gentleman who worked hard and loved his family."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=600",
                "description": "A lovely lady who enjoyed baking for those she loved."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=600",
                "description": "A cheerful man who always had a story to share."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=600",
                "description": "A gentle woman who found joy in every sunrise."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1474176857210-7287d38d27c6?w=600",
                "description": "A happy moment captured between old friends."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1542596594-649edbc13630?w=600",
                "description": "A couple dancing at a celebration from years ago."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600",
                "description": "A beautiful soul who brightened every room she entered."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1506869640319-fe1a24fd76cb?w=600",
                "description": "A man enjoying a quiet moment with his morning paper."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600",
                "description": "A young lady dressed elegantly for a special occasion."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1504257432389-52343af05a3c?w=600",
                "description": "A gentleman who took great pride in his garden."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1521119989659-a83eee488004?w=600",
                "description": "A man with a warm smile and a heart of gold."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1544005316-04ce1f0dfcbe?w=600",
                "description": "A woman enjoying a peaceful moment with her tea."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1554151228-14d9def656e4?w=600",
                "description": "A happy couple celebrating many years together."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1502823403499-6ccfcf4b453a?w=600",
                "description": "A kind-faced person who loved telling stories of the past."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=600",
                "description": "A cheerful gentleman who enjoyed a good laugh."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=600",
                "description": "A lovely woman with a passion for knitting."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=600",
                "description": "A distinguished man who loved classical music."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=600",
                "description": "A beautiful lady who always had cookies ready for visitors."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1552058544-f2b08422138a?w=600&sat=-50",
                "description": "A thoughtful soul who enjoyed watching the sunset."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&sat=-50",
                "description": "A friendly face that welcomed everyone to the neighborhood."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&sat=-50",
                "description": "A wise woman who shared wonderful stories with children."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&sat=-50",
                "description": "A proud grandfather showing old family photographs."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&sat=-50",
                "description": "A graceful lady who loved her afternoon walks."
            },
            {
                "image_url": "https://images.unsplash.com/photo-1504257432389-52343af05a3c?w=600&sat=-50",
                "description": "A happy man tending to his beloved rose garden."
            },
        ])
        
        # Use static fallback photos directly (source.unsplash.com is deprecated)
        photo = random.choice(fallback_photos)
        return {
            "image_url": photo["image_url"],
            "description": photo["description"]
        }
