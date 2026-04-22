from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.care_circle.providers.animal_friend.provider import AnimalFriendProvider
from app.services.care_circle.providers.ai_trivia.provider import AiTriviaProvider
from app.services.care_circle.providers.brain_booster.provider import BrainBoosterProvider
from app.services.care_circle.providers.classic_art.provider import ClassicArtProvider
from app.services.care_circle.providers.country_spotlight.provider import CountrySpotlightProvider
from app.services.care_circle.providers.finish_phrase.provider import FinishPhraseProvider
from app.services.care_circle.providers.famous_face.provider import FamousFaceProvider
from app.services.care_circle.providers.gratitude.provider import GratitudeProvider
from app.services.care_circle.providers.hymn_of_the_day.provider import HymnOfTheDayProvider
from app.services.care_circle.providers.missing_vowels.provider import MissingVowelsProvider
from app.services.care_circle.providers.morning_stretch.provider import MorningStretchProvider
from app.services.care_circle.providers.number_sequence.provider import NumberSequenceProvider
from app.services.care_circle.providers.odd_one_out.provider import OddOneOutProvider
from app.services.care_circle.providers.old_saying_match.provider import (
    OldSayingMatchProvider,
)
from app.services.care_circle.providers.puzzle.provider import PuzzleProvider
from app.services.care_circle.providers.simple_recipe.provider import SimpleRecipeProvider
from app.services.care_circle.providers.song_of_the_day.provider import SongOfTheDayProvider
from app.services.care_circle.providers.wikimedia_gallery.provider import (
    WikimediaGalleryProvider,
)
from app.services.care_circle.providers.word_of_the_day.provider import (
    WordOfTheDayProvider,
)
from app.services.care_circle.providers.word_scramble.provider import WordScrambleProvider


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


@pytest.mark.asyncio
async def test_wikimedia_gallery_uses_updated_garden_fallback_when_category_is_empty(monkeypatch):
    class DummyAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            return _DummyResponse({"query": {"categorymembers": []}})

    garden_theme = {
        "key": "gardens",
        "label": "Gardens",
        "category": "Featured pictures of gardens",
        "tagline": "Peaceful green spaces to enjoy.",
        "fallback": {
            "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Boston%20Public%20Garden%20%2836008p%29.jpg",
            "title": "Boston Public Garden",
            "description": "A graceful city garden offers flowers, trees, and a peaceful path to enjoy.",
            "credit": "Wikimedia Commons (featured picture)",
        },
    }

    monkeypatch.setattr(
        "app.services.care_circle.providers.wikimedia_gallery.provider.httpx.AsyncClient",
        lambda *args, **kwargs: DummyAsyncClient(),
    )
    monkeypatch.setattr(
        "app.services.care_circle.providers.wikimedia_gallery.provider.random.choice",
        lambda values: garden_theme,
    )

    provider = WikimediaGalleryProvider(patient_config={"themes": [garden_theme]})
    payload = await provider._generate_payload(
        SimpleNamespace(id=20, preferred_language="en")
    )

    assert payload["image_url"] == garden_theme["fallback"]["image_url"]
    assert payload["title"] == "Boston Public Garden"
    assert payload["theme_label"] == "Gardens"


def test_wikimedia_gallery_is_not_common_cached():
    provider = WikimediaGalleryProvider()
    assert provider.common is False


@pytest.mark.parametrize(
    ("provider_cls",),
    [
        (AiTriviaProvider,),
        (BrainBoosterProvider,),
        (FinishPhraseProvider,),
        (GratitudeProvider,),
        (MissingVowelsProvider,),
        (OddOneOutProvider,),
        (PuzzleProvider,),
        (SimpleRecipeProvider,),
        (SongOfTheDayProvider,),
        (WordScrambleProvider,),
    ],
)
def test_profile_dependent_providers_are_not_common_cached(provider_cls):
    provider = provider_cls()
    assert provider.common is False


@pytest.mark.parametrize(
    ("provider_cls",),
    [
        (ClassicArtProvider,),
        (CountrySpotlightProvider,),
        (FamousFaceProvider,),
        (HymnOfTheDayProvider,),
        (MorningStretchProvider,),
        (NumberSequenceProvider,),
        (OldSayingMatchProvider,),
        (WordOfTheDayProvider,),
    ],
)
def test_shared_static_providers_are_common_cached(provider_cls):
    provider = provider_cls()
    assert provider.common is True
