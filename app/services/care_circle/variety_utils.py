"""
Shared utilities for preventing repetition in care circle provider selections.

Two patterns:
  - date_seeded_choice: deterministic per-day selection (stable for re-renders,
    guaranteed to change each calendar day). Best for common providers.
  - pick_avoiding_recent: history-aware selection that excludes items seen in
    the last N days. Best for patient-specific providers with small pools.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import random
from pathlib import Path
from typing import Any, List, Optional

from app.services.care_circle.provider_cache import CACHE_ROOT

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Date-seeded deterministic selection
# ---------------------------------------------------------------------------

def date_seeded_choice(pool: List[Any], for_date: datetime.date) -> Any:
    """
    Choose one item from pool using a seed derived from for_date.

    Same date  → always the same item (idempotent re-renders).
    Different date → different item (cycles deterministically through pool).
    """
    if not pool:
        raise ValueError("pool must not be empty")
    seed = int(hashlib.md5(for_date.isoformat().encode()).hexdigest(), 16)
    rng = random.Random(seed)
    return rng.choice(pool)


def date_seeded_sample(pool: List[Any], k: int, for_date: datetime.date) -> List[Any]:
    """
    Choose k items from pool without replacement, seeded by for_date.
    """
    if not pool:
        raise ValueError("pool must not be empty")
    k = min(k, len(pool))
    seed = int(hashlib.md5(for_date.isoformat().encode()).hexdigest(), 16)
    rng = random.Random(seed)
    return rng.sample(pool, k)


# ---------------------------------------------------------------------------
# History-aware selection
# ---------------------------------------------------------------------------

def _history_path(
    provider_key: str,
    patient_id: Optional[int] = None,
) -> Path:
    if patient_id is not None:
        return CACHE_ROOT / str(patient_id) / "history" / f"{provider_key}.json"
    return CACHE_ROOT / "_history" / f"{provider_key}.json"


def _load_history(path: Path) -> List[str]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_history(path: Path, history: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history), encoding="utf-8")


def pick_avoiding_recent(
    pool: List[Any],
    provider_key: str,
    *,
    patient_id: Optional[int] = None,
    key_fn=None,
    lookback: Optional[int] = None,
) -> Any:
    """
    Choose one item from pool, avoiding items seen recently.

    Args:
        pool: list of items to choose from.
        provider_key: used to build the history file path.
        patient_id: if given, history is per-patient; otherwise system-wide.
        key_fn: callable that returns a string key from an item (default: str).
        lookback: how many recent selections to exclude (default: len(pool) - 1,
                  which means exhaust the full pool before repeating).

    Returns:
        A chosen item. Saves the choice to history for future calls.
    """
    if not pool:
        raise ValueError("pool must not be empty")

    if key_fn is None:
        key_fn = str

    if lookback is None:
        lookback = max(1, len(pool) - 1)

    path = _history_path(provider_key, patient_id)
    history = _load_history(path)
    recent = set(history[-lookback:])

    candidates = [item for item in pool if key_fn(item) not in recent]
    if not candidates:
        # All items have been seen recently — reset and use the full pool
        candidates = list(pool)
        history = []

    chosen = random.choice(candidates)
    history.append(key_fn(chosen))

    # Keep history bounded to avoid unbounded file growth (3× lookback max)
    max_history = lookback * 3
    if len(history) > max_history:
        history = history[-max_history:]

    _save_history(path, history)
    return chosen
