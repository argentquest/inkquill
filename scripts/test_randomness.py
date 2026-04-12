"""
Checks randomness of providers that pick from static lists.
Runs each provider 5 times and prints what was selected each time.
LLM calls are mocked so this runs fast.
"""
from __future__ import annotations
import asyncio
import os
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("APP_ENV", "development")

# ── mock LLM calls so we don't hit the API ────────────────────────────────────
async def _mock_text(*args, **kwargs):
    from app.services.care_circle.llm_helpers import LLMResponse
    return LLMResponse(content="MOCK_TEXT", model="mock")

async def _mock_json(*args, **kwargs):
    from app.services.care_circle.llm_helpers import LLMResponse
    return {}, LLMResponse(content="{}", model="mock")

async def _mock_image(*args, **kwargs):
    from app.services.care_circle.llm_helpers import LLMResponse
    return LLMResponse(content="https://mock.image/test.png", model="mock")

def install_mocks():
    import app.services.care_circle.llm_helpers as lh
    lh.generate_text_with_usage = _mock_text
    lh.generate_json_with_usage = _mock_json
    lh.generate_image_url_with_usage = _mock_image


class FakePatient:
    id = 1
    display_name = "Test Patient"
    first_name = "Test"
    last_name = "Patient"
    date_of_birth = None
    gender = None
    hobbies = []
    interests = []
    favorite_music = []
    hometown = None
    occupation = None
    religion = None
    notes = None


RUNS = 5

# Providers known to pick from static lists
STATIC_LIST_PROVIDERS = [
    "memory_lane_photo",
    "nature_scene",
    "daily_quote",
    "daily_affirmation",
    "joke",
    "cat_fact",
    "activity_suggestion",
    "gentle_exercise",
]


async def run_provider_n_times(key: str, n: int):
    import importlib, sys as _sys
    results = []
    for _ in range(n):
        mod_path = f"app.services.care_circle.providers.{key}.provider"
        if mod_path in _sys.modules:
            del _sys.modules[mod_path]
        try:
            mod = importlib.import_module(mod_path)
            class_name = "".join(w.title() for w in key.split("_")) + "Provider"
            cls = getattr(mod, class_name, None)
            if cls is None:
                return None
            instance = cls(patient_config={})
            result = await instance.execute(FakePatient())
            data = result.get("data", {})
            # Extract the most meaningful field to compare
            value = (
                data.get("image_url") or
                data.get("description") or
                data.get("quote") or
                data.get("text") or
                data.get("fact") or
                data.get("activity") or
                data.get("exercise") or
                str(data)
            )
            results.append(value[:80] if value else "(empty)")
        except Exception as e:
            results.append(f"ERROR: {e}")
    return results


async def main():
    install_mocks()
    patient = FakePatient()

    print(f"Running each provider {RUNS} times to check randomness...\n")

    for key in STATIC_LIST_PROVIDERS:
        results = await run_provider_n_times(key, RUNS)
        if results is None:
            print(f"[{key}] - provider class not found, skipping")
            continue

        unique = set(results)
        all_same = len(unique) == 1

        print(f"[{key}]")
        if all_same:
            print(f"  !! ALL {RUNS} RUNS RETURNED THE SAME VALUE !!")
            print(f"     {results[0]}")
        else:
            print(f"  OK - {len(unique)} unique results across {RUNS} runs")
            for i, r in enumerate(results, 1):
                print(f"  Run {i}: {r}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
