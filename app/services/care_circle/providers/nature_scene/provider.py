import logging
import random
from typing import Any, Dict

from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_image_url_with_usage,
    generate_text_with_usage,
)
from app.services.care_circle.provider_base import BaseCareCircleProvider

app_logger = logging.getLogger(__name__)


SCENE_THEME_SUGGESTIONS = [
    "a sunny garden filled with colourful roses and the hum of bees",
    "a calm lake at sunset with golden light on the water",
    "a meadow in spring with wildflowers and birdsong",
    "a gentle forest path with dappled sunlight through the trees",
    "a sandy beach with soft waves and the smell of the sea",
    "a snowy countryside lane lined with frosted trees",
    "an autumn orchard with red apples and falling leaves",
    "a cottage garden in summer with lavender and butterflies",
]

FALLBACK_SCENES = [
    {
        "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "description": "Warm sunlight settles over a peaceful lake, and the soft breeze carries the fresh scent of pine.",
    },
    {
        "image_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "description": "A flower meadow glows with yellow and blue blossoms while birds sing gently in the distance.",
    },
    {
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "description": "Sunlight filters through green trees along a quiet path, and the air smells cool and earthy.",
    },
    {
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "description": "Soft waves shine under a peach-coloured sky, and the sea breeze feels calm and refreshing.",
    },
]


def _choose_fallback_scene(theme: str, description: str) -> dict[str, str]:
    text = f"{theme} {description}".lower()
    if any(word in text for word in ["lake", "water", "river", "pond"]):
        return FALLBACK_SCENES[0]
    if any(word in text for word in ["flower", "garden", "meadow", "lavender", "rose"]):
        return FALLBACK_SCENES[1]
    if any(word in text for word in ["forest", "tree", "wood", "path", "orchard"]):
        return FALLBACK_SCENES[2]
    if any(word in text for word in ["beach", "sea", "ocean", "shore", "wave"]):
        return FALLBACK_SCENES[3]
    return random.choice(FALLBACK_SCENES)


class NatureSceneProvider(BaseCareCircleProvider):
    provider_key = "nature_scene"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config

        suggestions = "\n".join(f"- {suggestion}" for suggestion in SCENE_THEME_SUGGESTIONS)
        theme = random.choice(SCENE_THEME_SUGGESTIONS)
        try:
            theme_prompt = (
                "You are creating a calming nature scene for an elderly person.\n"
                "Here are some example scene themes for inspiration:\n"
                f"{suggestions}\n\n"
                "Generate ONE new peaceful nature scene theme, similar in style but "
                "different from all the examples above. It should evoke a specific season, "
                "time of day, or sensory detail (colour, sound, smell). "
                "Reply with only the scene description, one short phrase, no quotes, no explanation."
            )
            theme_resp = await generate_text_with_usage(theme_prompt, temperature=1.0)
            if theme_resp.content and len(theme_resp.content) > 5:
                theme = theme_resp.content.strip().rstrip(".")
        except Exception as exc:
            app_logger.error("LLM Error (nature_scene theme): %s", exc)

        description = None
        try:
            text_prompt = (
                f"Describe this peaceful scene in 2 short, warm sentences: {theme}. "
                "Mention one colour and one gentle sound or smell. "
                "Make it feel like a cozy, happy moment. "
                "Avoid storms, darkness, isolation, or anything that could feel lonely or distressing."
            )
            text_resp = await generate_text_with_usage(
                text_prompt,
                system=DEMENTIA_SYSTEM_PROMPT,
            )
            self.log_llm_response(
                text_resp,
                prompt=text_prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if text_resp.content and len(text_resp.content) > 10:
                description = text_resp.content
        except Exception as exc:
            app_logger.error("LLM Error (nature_scene text): %s", exc)

        if not description:
            fallbacks = cfg.get(
                "descriptions",
                [
                    "The garden is full of colour today. "
                    "You can almost smell the roses on the warm breeze."
                ],
            )
            description = random.choice(fallbacks)

        image_prompt = (
            f"Photorealistic, vibrant, peaceful nature scene: {theme}. "
            "Warm sunlight, rich colours, calming atmosphere, "
            "high detail, beautiful landscape photography."
        )
        try:
            ip_prompt = (
                "Turn this into a short image generation prompt (15 words max), "
                f'no people, peaceful outdoor scene: "{description}"'
            )
            ip_resp = await generate_text_with_usage(ip_prompt)
            if ip_resp.content and len(ip_resp.content) > 5:
                image_prompt = (
                    ip_resp.content.strip('"').strip()
                    + ", photorealistic, vibrant colours, warm sunlight, peaceful"
                )
        except Exception as exc:
            app_logger.error("LLM Error (nature_scene image prompt): %s", exc)

        image_url = ""
        try:
            img_resp = await generate_image_url_with_usage(image_prompt)
            self.log_llm_response(img_resp, prompt=image_prompt)
            image_url = img_resp.content
        except Exception as exc:
            app_logger.info(
                "Nature scene image generation unavailable, using fallback scene: %s",
                exc,
            )

        if not image_url:
            fallback_scene = _choose_fallback_scene(theme, description)
            image_url = fallback_scene["image_url"]
            description = fallback_scene["description"]

        return {
            "image_url": image_url,
            "description": description,
        }
