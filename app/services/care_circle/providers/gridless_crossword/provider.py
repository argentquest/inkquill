"""
Gridless Crossword Provider.

A daily word puzzle with 10 clues - first letters spell a secret word.
Uses LLM to generate themed word-clue pairs.
"""

from __future__ import annotations

import datetime
import random

import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


# In-memory daily cache for consistent puzzles per day
_daily_cache: dict[tuple, dict] = {}


class GridlessCrosswordProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Provides a daily gridless crossword puzzle with 10 word-clue pairs.
    The first letters of the answers spell a secret word.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """Generate the gridless crossword content."""
        cfg = self.patient_config
        
        # Get difficulty settings
        difficulty = self.difficulty_level
        diff_config = self.difficulty_config
        
        # Get today's category based on day of week
        today = datetime.datetime.now()
        day_of_week = str(today.weekday())
        category = cfg.get("day_categories", {}).get(day_of_week, "nature")
        
        # Create cache key based on date and difficulty
        cache_key = (today.date(), difficulty, category)
        
        # Check cache first
        if cache_key in _daily_cache:
            return _daily_cache[cache_key]
        
        # Get secret words for this category
        secret_words = cfg.get("secret_words", {}).get(category, ["TREASURE"])
        secret_word = random.choice(secret_words)
        
        # Generate the puzzle
        try:
            content = await self._generate_puzzle(
                category=category,
                secret_word=secret_word,
                diff_config=diff_config,
            )
        except Exception as e:
            app_logger.error(f"LLM Error (gridless_crossword): {e}")
            content = self._get_fallback(cfg)
        
        # Add metadata with scrambled word bank
        scrambled_words = [self._scramble_word(item["word"]) for item in content]
        result = {
            "category": category,
            "secret_word": secret_word,
            "difficulty": difficulty,
            "words": content,
            "scrambled_words": scrambled_words,
        }
        
        # Cache the result
        _daily_cache[cache_key] = result
        return result

    async def _generate_puzzle(
        self,
        category: str,
        secret_word: str,
        diff_config: dict,
    ) -> list[dict]:
        """Generate word-clue pairs via LLM."""
        
        min_len = diff_config.get("min_word_len", 4)
        max_len = diff_config.get("max_word_len", 8)
        
        # Build the prompt
        prompt = self._build_llm_prompt(
            category=category,
            secret_word=secret_word,
            min_len=min_len,
            max_len=max_len,
        )
        
        # Call LLM
        data, llm_response = await generate_json_with_usage(
            prompt,
            system=DEMENTIA_SYSTEM_PROMPT,
        )
        
        self.log_llm_response(
            llm_response,
            prompt=prompt,
            system_prompt=DEMENTIA_SYSTEM_PROMPT,
        )
        
        # Validate and return the words
        if data and "words" in data:
            words = data["words"]
            # Ensure we have exactly 10 words
            if len(words) >= 10:
                return words[:10]
            # Pad with fallback if needed
            fallback = self.config.get("fallback_words", [])
            while len(words) < 10 and fallback:
                words.append(fallback.pop(0))
            return words
        
        raise ValueError("Invalid LLM response format")

    def _build_llm_prompt(
        self,
        category: str,
        secret_word: str,
        min_len: int,
        max_len: int,
    ) -> str:
        """Build the LLM prompt for generating word-clue pairs."""
        
        category_hints = {
            "nature": "nature, animals, plants, weather, and the outdoors",
            "food": "food, cooking, restaurants, and culinary topics",
            "daily_life": "everyday objects, activities, and home life",
            "entertainment": "movies, music, games, and popular culture",
            "memories": "nostalgic topics, past events, and retro items",
        }
        
        hint = category_hints.get(category, "general knowledge")
        
        prompt = f"""Generate 10 word-clue pairs for a word puzzle.

THEME: {category} ({hint})
SECRET WORD: {secret_word}
The first letter of each answer must spell: {secret_word}

REQUIREMENTS:
- Each word must be {min_len}-{max_len} letters long
- Each clue should be clear and solvable for older adults
- Clues should be 1-2 sentences describing the word
- Return ONLY a JSON object with this exact format:
{{"words": [{{"word": "XXXXX", "clue": "Clue text..."}}, ...]}}

The 10 words must start with these letters in order: {secret_word}

Example format:
{{"words": [{{"word": "ORBIT", "clue": "The curved path of a celestial object."}}]}}

Generate exactly 10 word-clue pairs now:"""
        
        return prompt

    def _get_fallback(self, cfg: dict) -> list[dict]:
        """Get fallback words when LLM fails."""
        fallback = cfg.get("fallback_words", [])
        return random.sample(fallback, min(10, len(fallback)))

    def _scramble_word(self, word: str) -> str:
        """Scramble the letters of a word, keeping first and last letters in place."""
        if len(word) <= 3:
            return word
        # Scramble middle letters
        middle = list(word[1:-1])
        random.shuffle(middle)
        return word[0] + ''.join(middle) + word[-1]
