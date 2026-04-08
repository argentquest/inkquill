import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


SCENE_THEMES = [
    "a sunny garden filled with colourful roses and the hum of bees",
    "a calm lake at sunset with golden light on the water",
    "a meadow in spring with wildflowers and birdsong",
    "a gentle forest path with dappled sunlight through the trees",
    "a sandy beach with soft waves and the smell of the sea",
    "a snowy countryside lane lined with frosted trees",
    "an autumn orchard with red apples and falling leaves",
    "a cottage garden in summer with lavender and butterflies",
]


class NatureSceneProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Generates a calming nature scene: AI text description followed by
    an AI image generated from that same description.

    The image prompt is derived directly from the generated text so the
    image and description always match.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config

        # Pick a theme to anchor both the text and the image
        theme = random.choice(SCENE_THEMES)

        # ── Step 1: generate the descriptive text ─────────────────────
        description = None
        try:
            text_prompt = (
                f"Describe this peaceful scene in 2 short, warm sentences: {theme}. "
                "Mention one colour and one gentle sound or smell. "
                "Make it feel like a cozy, happy moment."
            )
            text_resp = await generate_text_with_usage(
                text_prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                text_resp, prompt=text_prompt, system_prompt=DEMENTIA_SYSTEM_PROMPT
            )
            if text_resp.content and len(text_resp.content) > 10:
                description = text_resp.content
        except Exception as e:
            app_logger.error(f"LLM Error (nature_scene text): {e}")

        if not description:
            fallbacks = cfg.get("descriptions", [
                "The garden is full of colour today. "
                "You can almost smell the roses on the warm breeze."
            ])
            description = random.choice(fallbacks)

        # ── Step 2: build image prompt from the description ───────────
        # Ask the LLM to turn the description into a crisp image prompt
        image_prompt = (
            f"Photorealistic, vibrant, peaceful nature scene: {theme}. "
            "Warm sunlight, rich colours, calming atmosphere, "
            "high detail, beautiful landscape photography."
        )
        try:
            ip_prompt = (
                f"Turn this into a short image generation prompt (15 words max), "
                f"no people, peaceful outdoor scene: \"{description}\""
            )
            ip_resp = await generate_text_with_usage(ip_prompt)
            if ip_resp.content and len(ip_resp.content) > 5:
                image_prompt = (
                    ip_resp.content.strip('"').strip()
                    + ", photorealistic, vibrant colours, warm sunlight, peaceful"
                )
        except Exception as e:
            app_logger.error(f"LLM Error (nature_scene image prompt): {e}")

        # ── Step 3: generate the image ────────────────────────────────
        image_url = ""
        try:
            img_resp = await generate_image_url_with_usage(image_prompt)
            self.log_llm_response(img_resp, prompt=image_prompt)
            image_url = img_resp.content
        except Exception as e:
            app_logger.error(f"Image generation error (nature_scene): {e}")

        if not image_url:
            w = cfg.get("image_width", 800)
            h = cfg.get("image_height", 500)
            image_url = f"https://picsum.photos/{w}/{h}?blur=1"

        return {
            "image_url": image_url,
            "description": description,
        }
