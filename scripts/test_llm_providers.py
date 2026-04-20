"""
Test each LLM provider to ensure fallback does not occur.
Runs each provider that uses LLM and verifies the LLM call succeeded.
"""

import asyncio
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict
from dataclasses import dataclass

# Setup path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("APP_ENV", "development")

from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    generate_text_with_usage,
    generate_json_with_usage,
    generate_image_url_with_usage,
    LLMResponse,
)

# Track LLM calls
llm_calls = []
original_generate_text = generate_text_with_usage
original_generate_json = generate_json_with_usage
original_generate_image = generate_image_url_with_usage


async def patched_generate_text(*args, **kwargs):
    try:
        result = await original_generate_text(*args, **kwargs)
        llm_calls.append({"type": "text", "success": True, "model": result.model, "tokens": result.total_tokens})
        return result
    except Exception as e:
        llm_calls.append({"type": "text", "success": False, "error": str(e)})
        raise


async def patched_generate_json(*args, **kwargs):
    try:
        data, result = await original_generate_json(*args, **kwargs)
        llm_calls.append({"type": "json", "success": True, "model": result.model, "tokens": result.total_tokens})
        return data, result
    except Exception as e:
        llm_calls.append({"type": "json", "success": False, "error": str(e)})
        raise


async def patched_generate_image(*args, **kwargs):
    try:
        result = await original_generate_image(*args, **kwargs)
        llm_calls.append({"type": "image", "success": True, "model": result.model})
        return result
    except Exception as e:
        llm_calls.append({"type": "image", "success": False, "error": str(e)})
        raise


# Patch the module
import app.services.care_circle.llm_helpers as lh
lh.generate_text_with_usage = patched_generate_text
lh.generate_json_with_usage = patched_generate_json
lh.generate_image_url_with_usage = patched_generate_image


@dataclass
class TestResult:
    provider_key: str
    success: bool
    llm_called: bool
    llm_succeeded: bool
    fallback_used: bool
    error: str = ""
    data_keys: list = None


def _to_camel(snake: str) -> str:
    return "".join(w.title() for w in snake.split("_"))


# Providers that use LLM
LLM_PROVIDERS = [
    "ai_trivia",
    "family_greeting",
    "gratitude",
    "hobby_spotlight",
    "letter_to_family",
    "local_history",
    "mindful_moment",
    "nostalgia",
    "pen_pal_letter",
    "personal_affirmation",
    "riddle",
    "seasonal_poem",
    "sensory",
    "simple_recipe",
    "song_of_the_day",
    "this_day_history",
    "world_news",
]


class MockPatientProfile:
    """Mock patient profile for testing."""
    def __init__(self):
        self.id = "test-patient-1"
        self.display_name = "Test Patient"
        self.preferences = {
            "preferences": {
                "era_of_youth": "1950s",
                "favorite_singers": ["Frank Sinatra"],
                "favorite_singer": "Frank Sinatra",
                "family_members": ["John", "Mary"],
                "hobbies": ["gardening", "reading"],
                "life_roles": ["teacher"],
                "pets": ["Buddy the dog"],
                "favourite_foods": ["apple pie"],
                "favourite_tv_shows": ["The Ed Sullivan Show"],
                "hometown": "Springfield",
                "nationality_or_background": "American",
                "city_for_weather": "London",
                "recipient_name": "Margaret",
                "preferred_pronoun": "she",
                "favorite_activities": ["knitting", "reading"],
                "mobility_level": "seated",
            },
            "recipient_name": "Margaret",
        }


async def test_provider(provider_key: str, patient: MockPatientProfile) -> TestResult:
    """Test a single provider and return results."""
    llm_calls.clear()
    
    module_path = f"app.services.care_circle.providers.{provider_key}.provider"
    if module_path in sys.modules:
        del sys.modules[module_path]
    
    try:
        module = importlib.import_module(module_path)
    except Exception as e:
        return TestResult(
            provider_key=provider_key,
            success=False,
            llm_called=False,
            llm_succeeded=False,
            fallback_used=False,
            error=f"Import error: {e}"
        )
    
    class_name = _to_camel(provider_key) + "Provider"
    cls = getattr(module, class_name, None)
    if cls is None:
        return TestResult(
            provider_key=provider_key,
            success=False,
            llm_called=False,
            llm_succeeded=False,
            fallback_used=False,
            error=f"Class {class_name} not found"
        )
    
    try:
        instance = cls(patient_config={})
        result = await instance.execute(patient)
        
        if not result.get("success", True):
            return TestResult(
                provider_key=provider_key,
                success=False,
                llm_called=len(llm_calls) > 0,
                llm_succeeded=any(c.get("success") for c in llm_calls),
                fallback_used=True,
                error=result.get("error_detail", "Provider returned failure"),
                data_keys=list(result.get("data", {}).keys()) if isinstance(result.get("data"), dict) else []
            )
        
        data = result.get("data", {})
        if isinstance(data, dict):
            data_keys = list(data.keys())
        else:
            data_keys = []
        
        # Check if fallback was used by looking at the data
        # If LLM was called and succeeded, fallback should not be used
        llm_called = len(llm_calls) > 0
        llm_succeeded = all(c.get("success") for c in llm_calls) if llm_called else False
        
        # Check if the result looks like a fallback
        fallback_used = False
        if llm_called and not llm_succeeded:
            fallback_used = True
        elif not llm_called:
            # Some providers don't call LLM at all (static providers)
            # This is expected for providers like word_of_the_day
            pass
        
        return TestResult(
            provider_key=provider_key,
            success=True,
            llm_called=llm_called,
            llm_succeeded=llm_succeeded,
            fallback_used=fallback_used,
            data_keys=data_keys
        )
        
    except Exception as e:
        return TestResult(
            provider_key=provider_key,
            success=False,
            llm_called=len(llm_calls) > 0,
            llm_succeeded=any(c.get("success") for c in llm_calls),
            fallback_used=True,
            error=str(e)
        )


async def main():
    print("=" * 70)
    print("Care Circle LLM Provider Test")
    print("=" * 70)
    print()
    
    patient = MockPatientProfile()
    results = []
    
    for provider_key in LLM_PROVIDERS:
        print(f"Testing {provider_key}...", end=" ", flush=True)
        result = await test_provider(provider_key, patient)
        results.append(result)
        
        if result.success and result.llm_succeeded and not result.fallback_used:
            print("OK (LLM succeeded)")
        elif result.success and result.fallback_used:
            print(f"FALLBACK USED - {result.error}")
        elif not result.success:
            print(f"FAILED - {result.error}")
        else:
            print("OK (no LLM call)")
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    ok_count = sum(1 for r in results if r.success and r.llm_succeeded and not r.fallback_used)
    fallback_count = sum(1 for r in results if r.fallback_used)
    failed_count = sum(1 for r in results if not r.success)
    
    print(f"Total providers tested: {len(results)}")
    print(f"LLM OK (no fallback):  {ok_count}")
    print(f"Fallback used:         {fallback_count}")
    print(f"Failed:                {failed_count}")
    
    if fallback_count > 0 or failed_count > 0:
        print()
        print("Providers needing fixes:")
        for r in results:
            if r.fallback_used or not r.success:
                status = "FALLBACK" if r.fallback_used else "FAILED"
                print(f"  [{status:8}] {r.provider_key}: {r.error}")
    
    print()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
