from types import SimpleNamespace

import pytest

from app.services.care_circle.llm_helpers import LLMResponse
from app.services.care_circle.providers.classic_art.provider import ClassicArtProvider
from app.services.care_circle.providers.nature_scene.provider import NatureSceneProvider


@pytest.mark.asyncio
async def test_nature_scene_uses_static_fallback_when_image_generation_unavailable(monkeypatch):
    async def fake_generate_text(*args, **kwargs):
        return LLMResponse(content="A bright garden path with birdsong")

    async def fake_generate_image(*args, **kwargs):
        raise RuntimeError("image backend unavailable")

    monkeypatch.setattr(
        "app.services.care_circle.providers.nature_scene.provider.generate_text_with_usage",
        fake_generate_text,
    )
    monkeypatch.setattr(
        "app.services.care_circle.providers.nature_scene.provider.generate_image_url_with_usage",
        fake_generate_image,
    )

    provider = NatureSceneProvider(patient_config={"image_width": 640, "image_height": 360})
    payload = await provider._generate_payload(SimpleNamespace(id=17))

    assert payload["image_url"].startswith("https://images.unsplash.com/")
    assert payload["description"]
    assert "garden" in payload["description"].lower() or "flower" in payload["description"].lower()


@pytest.mark.asyncio
async def test_classic_art_requests_met_with_descriptive_headers_and_falls_back(monkeypatch):
    captured = {}

    class DummyAsyncClient:
        def __init__(self, *args, **kwargs):
            captured["headers"] = kwargs.get("headers", {})

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *args, **kwargs):
            raise RuntimeError("met unavailable")

    monkeypatch.setattr(
        "app.services.care_circle.providers.classic_art.provider.httpx.AsyncClient",
        DummyAsyncClient,
    )
    monkeypatch.setattr(
        "app.services.care_circle.providers.classic_art.provider.random.choice",
        lambda values: values[0],
    )

    provider = ClassicArtProvider()
    payload = await provider._generate_payload(SimpleNamespace(id=17))

    assert "User-Agent" in captured["headers"]
    assert captured["headers"]["Accept"] == "application/json"
    assert payload["title"] == "The Starry Night"
    assert payload["image_url"].startswith("https://upload.wikimedia.org/")
