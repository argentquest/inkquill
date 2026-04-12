"""
Quick debug script for the nature_scene provider.
Patches generate_image_url_with_usage to print the exact prompt
sent to the image model before generating the image.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("APP_ENV", "development")


async def main():
    import app.services.care_circle.llm_helpers as lh
    from app.services.care_circle.llm_helpers import LLMResponse

    original_generate_image = lh.generate_image_url_with_usage

    async def _debug_generate_image(prompt: str) -> LLMResponse:
        print("\n" + "=" * 60)
        print("IMAGE PROMPT SENT TO MODEL:")
        print("-" * 60)
        print(prompt)
        print("=" * 60 + "\n")
        result = await original_generate_image(prompt)
        is_data_uri = result.content.startswith("data:")
        preview = result.content[:80] + "..." if len(result.content) > 80 else result.content
        print(f"IMAGE RESULT: {'data URI (b64)' if is_data_uri else 'URL'}")
        print(f"  {preview}")
        return result

    lh.generate_image_url_with_usage = _debug_generate_image

    # Minimal patient stub
    class FakePatient:
        id = 0
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

    from app.services.care_circle.providers.nature_scene.provider import NatureSceneProvider

    provider = NatureSceneProvider(patient_config={})
    result = await provider.execute(FakePatient())

    print("STATUS:", "OK" if result.get("success", True) else "FAILED")
    data = result.get("data", {})
    print("\nDESCRIPTION:")
    print(data.get("description", "(none)"))
    print("\nIMAGE URL:")
    print(data.get("image_url", "(none)"))


if __name__ == "__main__":
    asyncio.run(main())
