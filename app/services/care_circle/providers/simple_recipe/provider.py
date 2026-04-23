import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    get_dementia_system_prompt,
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from app.services.care_circle.variety_utils import pick_avoiding_recent
from typing import Any, Dict


RECIPE_CATEGORIES = [
    {"key": "baked_treat", "label": "a simple baked treat (biscuits, scones, or a small cake)"},
    {"key": "warm_drink", "label": "a comforting warm drink (cocoa, tea blend, or spiced milk)"},
    {"key": "simple_dessert", "label": "a no-bake dessert or sweet snack (pudding, fruit salad, or trifle)"},
    {"key": "soup_or_stew", "label": "a simple warming soup or stew"},
    {"key": "light_snack", "label": "a light savoury snack or sandwich filling"},
    {"key": "salad", "label": "a simple, fresh salad with easy-to-find ingredients"},
    {"key": "jam_or_preserve", "label": "a simple jam, compote, or fruit preserve (no complex canning required)"},
    {"key": "porridge_or_cereal", "label": "a warm, comforting porridge or cereal bowl with toppings"},
    {"key": "egg_dish", "label": "a simple egg dish (scrambled eggs, boiled eggs, or an omelette)"},
    {"key": "sandwich", "label": "a classic, nostalgic sandwich with a warm filling suggestion"},
    {"key": "cake_or_pudding", "label": "a classic sponge cake, bread pudding, or steamed pudding"},
    {"key": "cold_drink", "label": "a refreshing cold drink (lemonade, fruit cordial, or iced tea)"},
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
        prefs = self.get_patient_preferences(patient_profile)
        era = prefs.get("era_of_youth", "1950s")

        category = pick_avoiding_recent(RECIPE_CATEGORIES, "simple_recipe_category", key_fn=lambda x: x["key"])

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
                f"Think of {category['label']} from the {era}. "
                f"It should use common ingredients everyone has at home. "
                f"Avoid exotic, expensive, or hard-to-find ingredients. "
                f"The steps should be very short and easy to follow (3-4 steps max). "
                f"Each step should be one short sentence. "
                f"Ensure all steps are safe and simple — no sharp knives, hot oil, or complex techniques. "
                f'Return as JSON: {{"name": "...", "ingredients": "...", "steps": "..."}}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=get_dementia_system_prompt(self.get_generation_date())
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=get_dementia_system_prompt(self.get_generation_date()),
            )
            if data.get("name") and data.get("steps"):
                return data
        except Exception as e:
            app_logger.error(f"LLM Error (simple_recipe): {e}")

        recipes = cfg.get(
            "recipes",
            [
                {"name": "Classic Hot Cocoa", "ingredients": "Milk, cocoa powder, sugar", "steps": "Warm milk, stir in cocoa and sugar, enjoy!"},
                {"name": "Buttered Toast with Jam", "ingredients": "Bread, butter, jam", "steps": "Toast the bread, spread butter while warm, add your favourite jam."},
                {"name": "Simple Egg on Toast", "ingredients": "Egg, bread, butter", "steps": "Boil an egg for 5 minutes, toast the bread, butter it, and place the egg on top."},
                {"name": "Warm Honey Milk", "ingredients": "Milk, honey", "steps": "Warm the milk in a pan, stir in a teaspoon of honey, and pour into a cup."},
                {"name": "Classic Fruit Salad", "ingredients": "Apple, banana, orange, grapes", "steps": "Peel and slice the fruit, mix in a bowl, and serve with a sprinkle of sugar."},
                {"name": "Lemon Barley Water", "ingredients": "Barley, lemon, sugar, water", "steps": "Simmer barley in water for 20 minutes, strain, add lemon juice and sugar, chill."},
                {"name": "Bread and Butter Pudding", "ingredients": "Bread, butter, eggs, milk, sugar, raisins", "steps": "Butter the bread and layer in a dish. Pour over beaten egg and milk. Scatter raisins and sugar, then bake for 30 minutes."},
                {"name": "Simple Tomato Soup", "ingredients": "Tinned tomatoes, onion, stock, cream", "steps": "Soften onion in a pan, add tomatoes and stock, simmer 15 minutes, blend until smooth, stir in cream."},
                {"name": "Cucumber Sandwiches", "ingredients": "Bread, butter, cucumber, salt", "steps": "Butter the bread, layer thin slices of cucumber, add a pinch of salt, and cut into triangles."},
                {"name": "Rice Pudding", "ingredients": "Rice, milk, sugar, nutmeg", "steps": "Combine rice, milk and sugar in a baking dish. Sprinkle with nutmeg and bake for 1 hour, stirring twice."},
            ],
        )
        return pick_avoiding_recent(recipes, "simple_recipe_fallback", key_fn=lambda x: x["name"])
