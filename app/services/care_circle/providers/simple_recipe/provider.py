import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from typing import Any, Dict


RECIPE_CATEGORIES = [
    {
        "key": "baked_treat",
        "label": "a simple baked treat (biscuits, scones, or a small cake)",
    },
    {
        "key": "warm_drink",
        "label": "a comforting warm drink (cocoa, tea blend, or spiced milk)",
    },
    {
        "key": "simple_dessert",
        "label": "a no-bake dessert or sweet snack (pudding, fruit salad, or trifle)",
    },
    {
        "key": "soup_or_stew",
        "label": "a simple warming soup or stew",
    },
    {
        "key": "light_snack",
        "label": "a light savoury snack or sandwich filling",
    },
]


class SimpleRecipeProvider(BaseCareCircleProvider):
    provider_key = "simple_recipe"
    is_safe_for_patient = True

    """
    Generates a very simple, nostalgic recipe with 3-4 steps using an LLM.

    Rotates across five recipe categories (baked treat, warm drink, simple
    dessert, soup/stew, light snack) to keep content fresh day to day.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        era = prefs.get("era_of_youth", "1950s")

        category = random.choice(RECIPE_CATEGORIES)

        try:
            prompt = (
                f"Think of {category['label']} from the {era}. "
                f"It should use common ingredients everyone has at home. "
                f"Avoid exotic, expensive, or hard-to-find ingredients. "
                f"The steps should be very short and easy to follow (3-4 steps max). "
                f"Each step should be one short sentence. "
                f"Ensure all steps are safe and simple — no sharp knives, hot oil, or complex techniques. "
                f'Return as JSON: {{"name": "...", "ingredients": "...", "steps": "..."}}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if data.get("name") and data.get("steps"):
                return data
        except Exception as e:
            app_logger.error(f"LLM Error (simple_recipe): {e}")

        recipes = cfg.get(
            "recipes",
            [
                {
                    "name": "Classic Hot Cocoa",
                    "ingredients": "Milk, cocoa powder, sugar",
                    "steps": "Warm milk, stir in cocoa and sugar, enjoy!",
                }
            ],
        )
        return random.choice(recipes)
