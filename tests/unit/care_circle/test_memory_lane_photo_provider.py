import pytest

from app.services.care_circle.providers.memory_lane_photo.provider import (
    MemoryLanePhotoProvider,
    _build_search_queries,
    _choose_best_match,
    _score_candidate,
)
from app.services.care_circle.llm_helpers import LLMResponse


def test_memory_lane_photo_scores_specific_hometown_results_above_generic_collages():
    specific_score = _score_candidate(
        "Montreal street scene, 1960",
        "A quiet neighborhood street in Montreal during the 1960s.",
        query_terms={"montreal", "street", "scene", "1960s"},
        theme_terms={"peaceful", "everyday", "neighborhood", "street", "montreal", "1960s"},
        hometown_terms={"montreal"},
        era_terms={"1960", "1960s"},
    )
    generic_score = _score_candidate(
        "1960 image collage",
        "A collage of assorted images from 1960.",
        query_terms={"montreal", "street", "scene", "1960s"},
        theme_terms={"peaceful", "everyday", "neighborhood", "street", "montreal", "1960s"},
        hometown_terms={"montreal"},
        era_terms={"1960", "1960s"},
    )

    assert specific_score > generic_score


@pytest.mark.asyncio
async def test_memory_lane_photo_choose_best_match_prefers_specific_result(monkeypatch):
    results = [
        {"title": "File:1960_Image_Collage.jpg"},
        {"title": "File:Montreal_street_scene_1960.jpg"},
    ]

    async def fake_fetch(title: str) -> dict:
        if "Collage" in title:
            return {
                "image_url": "https://example.com/collage.jpg",
                "raw_title": "1960 image collage",
                "raw_description": "A collage of assorted images from 1960.",
            }
        return {
            "image_url": "https://example.com/montreal.jpg",
            "raw_title": "Montreal street scene, 1960",
            "raw_description": "A peaceful neighborhood street in Montreal during the 1960s.",
        }

    monkeypatch.setattr(
        "app.services.care_circle.providers.memory_lane_photo.provider._fetch_image_info",
        fake_fetch,
    )

    best = await _choose_best_match(
        results,
        search_query="Montreal street scene 1960s",
        theme="A peaceful, everyday neighborhood street in Montreal from the 1960s.",
        hometown="Montreal, Quebec",
        era="1960",
    )

    assert best["image_url"] == "https://example.com/montreal.jpg"


def test_memory_lane_photo_builds_location_aware_query_candidates():
    queries = _build_search_queries(
        llm_query="Montreal street scene 1960s",
        hometown="Montreal, Quebec",
        era="1960",
        theme="A warm, everyday neighborhood street scene in Montreal from the 1960s.",
        background="Canadian",
        hobbies_str="Engineering, Gardening",
    )

    assert queries[0] == "Montreal street scene 1960s"
    assert "Montreal neighborhood 1960s" in queries
    assert "Montreal Quebec street scene 1960s" in queries
    assert "Montreal old photo 1960s" in queries


@pytest.mark.asyncio
async def test_memory_lane_photo_records_token_usage_for_both_json_calls(monkeypatch):
    provider = MemoryLanePhotoProvider()
    patient = type(
        "Patient",
        (),
        {
            "id": 20,
            "display_name": "Denise Rivard",
            "preferences": {
                "era_of_youth": "1960",
                "hometown": "Montreal, Quebec",
                "nationality_or_background": "Canadian",
                "hobbies": ["Gardening"],
            },
        },
    )()

    responses = [
        (
            {"search_query": "Montreal street scene 1960s", "theme": "warm neighborhood life"},
            LLMResponse(content='{"search_query":"Montreal street scene 1960s","theme":"warm neighborhood life"}', prompt_tokens=10, completion_tokens=5, total_tokens=15, model="gpt-test"),
        ),
        (
            {"caption": "A warm memory of everyday neighborhood life in Montreal."},
            LLMResponse(content='{"caption":"A warm memory of everyday neighborhood life in Montreal."}', prompt_tokens=20, completion_tokens=10, total_tokens=30, model="gpt-test"),
        ),
    ]

    async def fake_generate_json_with_usage(*args, **kwargs):
        return responses.pop(0)

    async def fake_search(query: str):
        return [{"title": "File:Montreal_street_scene_1960.jpg"}]

    async def fake_choose_best_match(*args, **kwargs):
        return {
            "image_url": "https://example.com/montreal.jpg",
            "raw_title": "Montreal street scene, 1960",
            "raw_description": "A peaceful neighborhood street in Montreal during the 1960s.",
        }

    monkeypatch.setattr(
        "app.services.care_circle.providers.memory_lane_photo.provider.generate_json_with_usage",
        fake_generate_json_with_usage,
    )
    monkeypatch.setattr(
        "app.services.care_circle.providers.memory_lane_photo.provider._search_wikimedia",
        fake_search,
    )
    monkeypatch.setattr(
        "app.services.care_circle.providers.memory_lane_photo.provider._choose_best_match",
        fake_choose_best_match,
    )

    result = await provider.execute(patient)

    assert result["success"] is True
    assert result["token_usage"]["prompt_tokens"] == 30
    assert result["token_usage"]["completion_tokens"] == 15
    assert result["token_usage"]["total_tokens"] == 45
    assert result["token_usage"]["model"] == "gpt-test"
