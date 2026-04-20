from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.care_circle.providers.animal_friend.provider import AnimalFriendProvider
from app.services.care_circle.providers.wikimedia_gallery.provider import (
    WikimediaGalleryProvider,
)


class _DummyResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"status {self.status_code}")

    def json(self) -> dict:
        return self._payload


@pytest.mark.asyncio
async def test_provider_catalog_seed_updates_enabled_and_visibility_flags():
    from app.crud import care_circle as care_circle_crud

    existing = MagicMock()
    existing.provider_key = "gnews"
    existing.label = "News"
    existing.icon = "news"
    existing.category = "core"
    existing.enabled = True
    existing.display_order = 28
    existing.patient_visible = True
    existing.family_visible = True

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [existing]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    provider_inventory = [
        {
            "provider_key": "gnews",
            "label": "News",
            "icon": "news",
            "category": "core",
            "enabled": False,
            "display_order": 28,
            "patient_visible": False,
            "family_visible": False,
        }
    ]

    with patch.object(
        care_circle_crud,
        "remove_obsolete_provider_data",
        new=AsyncMock(),
    ), patch.object(
        care_circle_crud,
        "_load_provider_catalog_inventory",
        return_value=provider_inventory,
    ):
        await care_circle_crud.ensure_provider_catalog_seeded(mock_db)

    assert existing.enabled is False
    assert existing.patient_visible is False
    assert existing.family_visible is False
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_animal_friend_uses_dog_facts_with_dog_image(monkeypatch):
    class DummyAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *args, **kwargs):
            return _DummyResponse({"message": "https://images.example/dog.jpg"})

    monkeypatch.setattr(
        "app.services.care_circle.providers.animal_friend.provider.httpx.AsyncClient",
        lambda *args, **kwargs: DummyAsyncClient(),
    )

    provider = AnimalFriendProvider(
        patient_config={"dog_facts": ["Dogs love companionship and gentle routines."]}
    )
    payload = await provider._generate_payload(SimpleNamespace(id=20))

    assert payload["animal"] == "Dog"
    assert payload["image_url"] == "https://images.example/dog.jpg"
    assert payload["fact"] == "Dogs love companionship and gentle routines."


@pytest.mark.asyncio
async def test_wikimedia_gallery_filters_non_latin_metadata_for_english_patients(monkeypatch):
    class DummyAsyncClient:
        def __init__(self, *args, **kwargs):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            self.calls += 1
            if params and params.get("list") == "categorymembers":
                return _DummyResponse(
                    {
                        "query": {
                            "categorymembers": [
                                {"title": "File:arabic.jpg"},
                                {"title": "File:english.jpg"},
                            ]
                        }
                    }
                )
            if params and params.get("titles") == "File:arabic.jpg":
                return _DummyResponse(
                    {
                        "query": {
                            "pages": {
                                "1": {
                                    "imageinfo": [
                                        {
                                            "thumburl": "https://images.example/arabic.jpg",
                                            "extmetadata": {
                                                "ObjectName": {"value": "صورة قديمة"},
                                                "ImageDescription": {"value": "منظر جميل"},
                                                "Artist": {"value": "مصور"},
                                                "LicenseShortName": {"value": "CC BY-SA 4.0"},
                                            },
                                        }
                                    ]
                                }
                            }
                        }
                    }
                )
            return _DummyResponse(
                {
                    "query": {
                        "pages": {
                            "2": {
                                "imageinfo": [
                                    {
                                        "thumburl": "https://images.example/english.jpg",
                                        "extmetadata": {
                                            "ObjectName": {"value": "Sunny Garden"},
                                            "ImageDescription": {
                                                "value": "A peaceful garden path with roses."
                                            },
                                            "Artist": {"value": "Jane Smith"},
                                            "LicenseShortName": {"value": "CC BY-SA 4.0"},
                                        },
                                    }
                                ]
                            }
                        }
                    }
                }
            )

    monkeypatch.setattr(
        "app.services.care_circle.providers.wikimedia_gallery.provider.httpx.AsyncClient",
        lambda *args, **kwargs: DummyAsyncClient(),
    )
    monkeypatch.setattr(
        "app.services.care_circle.providers.wikimedia_gallery.provider.random.choice",
        lambda values: values[0],
    )
    monkeypatch.setattr(
        "app.services.care_circle.providers.wikimedia_gallery.provider.random.sample",
        lambda values, k: values[:k],
    )

    provider = WikimediaGalleryProvider()
    payload = await provider._generate_payload(
        SimpleNamespace(id=20, preferred_language="en")
    )

    assert payload["image_url"] == "https://images.example/english.jpg"
    assert payload["title"] == "Sunny Garden"
    assert "peaceful garden path" in payload["description"]
