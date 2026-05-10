import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from app.services.care_circle.variety_utils import pick_avoiding_recent
from typing import Any, Dict


NOSTALGIA_TOPICS = [
    {"key": "food", "hint": "Focus on a popular food, meal, or treat that people enjoyed back then — something from a kitchen, bakery, or family dinner table."},
    {"key": "music_dance", "hint": "Focus on the music or dancing from that era — a dance style, a radio show, a favourite song, or a jukebox."},
    {"key": "neighbourhood", "hint": "Focus on neighbourhood life — a corner shop, children playing outside, a street game, or a familiar community gathering."},
    {"key": "fashion", "hint": "Focus on fashion or style from that time — clothing, hairstyles, hats, or getting dressed up for a special occasion."},
    {"key": "entertainment", "hint": "Focus on entertainment from that era — a favourite TV or radio show, a cinema trip, or a popular game."},
    {"key": "school_or_work", "hint": "Focus on school days or everyday working life from that time — a classroom memory, a lunch break, or a simple daily routine."},
    {"key": "holidays", "hint": "Focus on a holiday or vacation from that time — a seaside trip, a family outing, or a festive celebration."},
    {"key": "sports", "hint": "Focus on a popular sport or outdoor game from that era — watching a match, playing in the park, or a local team they followed."},
    {"key": "home_life", "hint": "Focus on everyday home life — household chores, kitchen smells, a favourite room, or the sounds of a busy household."},
    {"key": "celebrations", "hint": "Focus on a celebration or special occasion — a birthday party, a wedding, a graduation, or a festive gathering."},
    {"key": "friendship", "hint": "Focus on friendship and community — a best friend, neighbours helping each other, or a local club or group."},
    {"key": "transport", "hint": "Focus on how people got around back then — buses, bicycles, trains, or the family car on a day out."},
    {"key": "garden_nature", "hint": "Focus on gardens, parks, or nature from that time — growing vegetables, picking fruit, or sitting outside in fine weather."},
    {"key": "crafts_hobbies", "hint": "Focus on a popular hobby or craft from that era — knitting, woodworking, painting, or collecting something beloved."},
    {"key": "shopping", "hint": "Focus on shopping from that time — a favourite local shop, market stalls, or the weekly grocery run."},
    {"key": "seasons", "hint": "Focus on how a particular season felt back then — a hot summer's day, the first snow, autumn leaves, or spring flowers."},
    {"key": "childhood_games", "hint": "Focus on the games children played back then — outdoor games in the street, board games on a rainy day, or a favourite toy."},
    {"key": "animals_pets", "hint": "Focus on animals or pets from that time — a beloved family pet, farm animals, or wildlife they remember fondly."},
    {"key": "reading_learning", "hint": "Focus on reading, learning, or stories from that era — a favourite book, a library visit, or something they loved to learn about."},
    {"key": "kitchen_cooking", "hint": "Focus on cooking or baking from that time — a recipe passed down, a Sunday roast smell, or helping in the kitchen as a child."},
]


class NostalgiaProvider(BaseCareCircleProvider):
    provider_key = "nostalgia"
    is_safe_for_patient = True

    """
    Generates personalized nostalgic memories using a Large Language Model.

    Rotates across six topic areas (food, music/dance, neighbourhood, fashion,
    entertainment, school/work) to bring different warm memories each day.
    Personalises with nationality, hometown, life roles, favourite foods and
    TV shows when available.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        prefs = self.get_patient_preferences(patient_profile)
        default_era = cfg.get("default_era", "1950s")
        era = prefs.get("era_of_youth", default_era) or default_era
        name = self.get_recipient_name(patient_profile, default="friend")

        nationality = prefs.get("nationality_or_background", "")
        hometown = prefs.get("hometown", "")
        life_roles = prefs.get("life_roles", [])
        favourite_foods = prefs.get("favourite_foods", [])
        favourite_tv_shows = prefs.get("favourite_tv_shows", [])

        patient_id = getattr(patient_profile, "id", None) if patient_profile else None
        topic = pick_avoiding_recent(
            NOSTALGIA_TOPICS,
            "nostalgia_topic",
            patient_id=patient_id,
            key_fn=lambda x: x["key"],
        )

        # Build optional context lines to enrich the prompt
        context_parts = []
        if nationality:
            context_parts.append(f"They have a {nationality} background.")
        if hometown:
            context_parts.append(f"They grew up in {hometown}.")
        if life_roles:
            context_parts.append(
                f"They were a {', '.join(life_roles[:2])}."
            )
        if topic["key"] == "food" and favourite_foods:
            context_parts.append(
                f"Foods they loved: {', '.join(favourite_foods[:2])}."
            )
        if topic["key"] == "entertainment" and favourite_tv_shows:
            context_parts.append(
                f"Shows they enjoyed: {', '.join(favourite_tv_shows[:2])}."
            )
        context_str = " ".join(context_parts)

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
                f"Write a happy memory from the {era} for {name}. "
                f"{topic['hint']} "
                f"{context_str} "
                f"Keep it to 2 short sentences. Make it feel cozy and familiar. "
                f"Avoid any memories of loss, hardship, war, illness, or distressing events. "
                f"Focus only on warm, joyful, universally positive experiences."
            )
            llm_response = await generate_text_with_usage(
                prompt, system=self.get_system_prompt(patient_profile)
            )
            self.log_llm_response(
                llm_response,
                prompt=prompt,
                system_prompt=self.get_system_prompt(patient_profile),
            )
            if llm_response.content and len(llm_response.content) > 10:
                return {"nostalgia": llm_response.content}
        except Exception as e:
            app_logger.error(f"LLM Error (nostalgia): {e}")

        facts = cfg.get("facts", {})
        fallback = cfg.get(
            "fallback",
            "Do you remember the wonderful music and dances from your youth?",
        )
        era_facts = facts.get(era, [fallback])
        if isinstance(era_facts, list):
            return {"nostalgia": pick_avoiding_recent(era_facts, "nostalgia_fallback", patient_id=patient_id)}
        return {"nostalgia": era_facts}
