import pytest

from app.services.care_circle.providers.memory_lane_photo.provider import (
    _build_search_queries,
    _choose_best_match,
    _score_candidate,
)


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
