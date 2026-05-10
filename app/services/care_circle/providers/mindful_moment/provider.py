"""
Mindful Moment provider for Care Circle patient sessions.
Uses an LLM to generate a personalised short mindfulness or breathing exercise.
Falls back to a curated static pool if LLM is unavailable.
"""

import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    generate_json_with_usage,
)
from app.services.care_circle.variety_utils import pick_avoiding_recent

logger = logging.getLogger(__name__)


EXERCISE_TYPES = [
    {
        "key": "breathing",
        "label": "a simple, calming breathing exercise",
        "example": "Breathe in slowly for 4 counts, hold for 2, breathe out for 6.",
    },
    {
        "key": "body_scan",
        "label": "a brief seated body scan — noticing how each part of the body feels",
        "example": "Notice your feet on the floor, your hands on your lap, and take a slow breath.",
    },
    {
        "key": "five_senses",
        "label": "a gentle five-senses grounding exercise",
        "example": "Name one thing you can see, hear, feel, smell, and taste right now.",
    },
    {
        "key": "visualisation",
        "label": "a short peaceful visualisation — imagining a calm, beautiful place",
        "example": "Close your eyes and picture sitting in a sunny garden full of flowers.",
    },
    {
        "key": "gratitude_breath",
        "label": "a gratitude breathing moment — breathing in something good, breathing out tension",
        "example": "Breathe in warmth and love; breathe out any worries.",
    },
    {
        "key": "finger_breathing",
        "label": "a finger-tracing breathing exercise — tracing each finger up and down with the breath",
        "example": "Trace slowly up each finger as you breathe in, and down as you breathe out.",
    },
    {
        "key": "warm_hands",
        "label": "a warm-hands relaxation — rubbing the palms together to create warmth",
        "example": "Rub your palms together, hold them over your cheeks, and breathe in the warmth.",
    },
    {
        "key": "shoulder_release",
        "label": "a gentle shoulder-release moment — lifting and dropping the shoulders with the breath",
        "example": "Breathe in and lift your shoulders to your ears, then drop them as you breathe out.",
    },
    {
        "key": "colour_breathing",
        "label": "a colour-breathing exercise — imagining breathing in a favourite calming colour",
        "example": "Imagine breathing in a soft golden light that fills you with peace.",
    },
    {
        "key": "sound_awareness",
        "label": "a gentle sound-awareness moment — simply listening to what can be heard around you",
        "example": "Close your eyes, listen quietly, and notice three different sounds in the room.",
    },
    {
        "key": "smile_breath",
        "label": "a smile-and-breathe exercise — smiling gently while breathing slowly",
        "example": "Let a gentle smile come to your face and breathe in slowly. Feel how warmth spreads through you.",
    },
    {
        "key": "counting_blessings",
        "label": "a counting-blessings breath — breathing in gratitude for people and places you love",
        "example": "Breathe in and think of someone you love; breathe out and feel grateful.",
    },
]

FALLBACK_EXERCISES = [
    {
        "title": "Peaceful Breathing",
        "instruction": (
            "Sit comfortably with your hands resting gently on your lap. "
            "Take a slow breath in through your nose for 4 counts. "
            "Hold softly for 2 counts. "
            "Breathe out slowly through your mouth for 6 counts. "
            "Repeat this 5 times and notice how calm and relaxed you feel."
        ),
        "duration_note": "Takes about 2 minutes.",
    },
    {
        "title": "Notice and Breathe",
        "instruction": (
            "Look around the room and notice one thing that is beautiful or makes you smile. "
            "Take a deep, slow breath in while you look at it. "
            "Breathe out slowly and let your shoulders drop and relax. "
            "Do this 3 times. Let yourself simply enjoy the moment."
        ),
        "duration_note": "Takes about 1 minute.",
    },
    {
        "title": "Warm Hands Exercise",
        "instruction": (
            "Rub your palms together gently until they feel warm. "
            "Place them softly over your eyes or cheeks and take a slow breath. "
            "Feel the warmth and let your face relax completely. "
            "Hold for a moment, then lower your hands to your lap. "
            "Repeat twice more."
        ),
        "duration_note": "Takes about 1-2 minutes.",
    },
    {
        "title": "Peaceful Garden Visualisation",
        "instruction": (
            "Close your eyes and imagine you are sitting in a beautiful, sunny garden. "
            "Flowers are blooming in every colour, and you can hear birds singing softly. "
            "Feel the warm sunshine on your face. "
            "Take a long, slow breath and enjoy this peaceful place for a moment."
        ),
        "duration_note": "Takes about 2-3 minutes.",
    },
    {
        "title": "Finger Breathing",
        "instruction": (
            "Hold one hand up, fingers spread wide. "
            "Use the finger of your other hand to slowly trace up the outside of your thumb as you breathe in. "
            "Trace down the inside of your thumb as you breathe out. "
            "Continue along each finger — breathing in as you go up, out as you go down. "
            "By the time you reach your little finger, you will feel wonderfully calm."
        ),
        "duration_note": "Takes about 2 minutes.",
    },
    {
        "title": "Counting Blessings Breath",
        "instruction": (
            "Take a slow, deep breath in, and think of one person you love. "
            "Breathe out slowly and feel gratitude for them. "
            "Take another breath in, and think of one place you have always loved. "
            "Breathe out and smile as you picture it. "
            "Take one more breath in, and think of something that makes you happy today. "
            "Breathe out gently. Rest quietly for a moment."
        ),
        "duration_note": "Takes about 2-3 minutes.",
    },
]


class MindfulMomentProvider(BaseCareCircleProvider):
    provider_key = "mindful_moment"
    is_safe_for_patient = True

    """
    Generates a short, personalised mindfulness or breathing exercise using an LLM.
    Falls back to a curated static pool of 6 exercises if the LLM is unavailable.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        exercise_type = pick_avoiding_recent(EXERCISE_TYPES, "mindful_moment_type", key_fn=lambda x: x["key"])

        try:
            d = self.get_generation_date()
            today_str = f"{d.strftime('%B')} {d.day}, {d.year}"
            prompt = (
                f"Today is {today_str}. "
                f"Create {exercise_type['label']} for a senior person. "
                f"It must be very gentle, calming, and easy to follow from a chair. "
                f"Write the instruction as a single short paragraph in a warm, soothing tone. "
                f"Keep it to 3-5 sentences maximum. "
                f"Example style: {exercise_type['example']} "
                f"Return as JSON: "
                '{"title": "...", "instruction": "...", "duration_note": "Takes about X minutes."}'
            )
            data, llm_response = await generate_json_with_usage(
                prompt, system=self.get_system_prompt(patient_profile)
            )
            self.log_llm_response(llm_response, prompt=prompt, system_prompt=self.get_system_prompt(patient_profile))
            if data.get("title") and data.get("instruction"):
                return data
        except Exception as e:
            logger.error(f"LLM Error (mindful_moment): {e}")

        fallback_pool = cfg.get("exercises", FALLBACK_EXERCISES)
        return pick_avoiding_recent(fallback_pool, "mindful_moment_fallback", key_fn=lambda x: x["title"])
