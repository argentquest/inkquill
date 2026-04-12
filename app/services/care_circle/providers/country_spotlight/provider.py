"""
Country Spotlight provider for Care Circle patient sessions.
Delivers a fun fact card about a different country from a large curated pool.
Static provider — no LLM or external calls required.
"""

import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)

# Path to external data file
_DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "country_spotlight.json"

# Lazy-loaded country pool
_countries_cache: List[Dict[str, str]] = []


def _load_countries() -> List[Dict[str, str]]:
    """Load country data from external JSON file with fallback."""
    global _countries_cache
    if _countries_cache:
        return _countries_cache

    try:
        if _DATA_FILE.exists():
            _countries_cache = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
            if _countries_cache:
                return _countries_cache
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load country data from %s: %s", _DATA_FILE, exc)

    # Minimal fallback
    _countries_cache = [
        {"country": "Italy", "flag": "🇮🇹", "capital": "Rome", "fun_fact": "Italy is home to more UNESCO World Heritage Sites than any other country in the world!"},
        {"country": "Japan", "flag": "🇯🇵", "capital": "Tokyo", "fun_fact": "Japan has over 6,800 islands!"},
        {"country": "Canada", "flag": "🇨🇦", "capital": "Ottawa", "fun_fact": "Canada has more lakes than all other countries in the world combined!"},
    ]
    return _countries_cache


class CountrySpotlightProvider(BaseCareCircleProvider):
    provider_key = "country_spotlight"
    is_safe_for_patient = True

    """
    Delivers a fun fact card about a world country from a curated pool of 50 entries.
    Pure static provider — data loaded from external JSON file.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        # Allow config override, otherwise load from external data file
        pool = cfg.get("countries") or _load_countries()
        entry = random.choice(pool)
        return {
            "country": entry["country"],
            "flag": entry["flag"],
            "capital": entry["capital"],
            "fun_fact": entry["fun_fact"],
        }
