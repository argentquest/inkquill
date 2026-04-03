import base64
import time

import pytest
from sqlalchemy import select

from app.models.generated_image import GeneratedImage
from app.models.job_status import JobStateEnum, JobStatus
from app.services.image_providers.base_provider import ImageGenerationResult


pytestmark = pytest.mark.integration


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO5lmNcAAAAASUVORK5CYII="
)


def test_async_image_generation_job_with_mocked_provider(
    client,
    register_and_login,
    run_db,
    app_instance,
    monkeypatch,
):
    async def fake_generate_image_with_active_provider(prompt: str, user_id_for_log: int, size: str = None):
        del user_id_for_log, size
        return ImageGenerationResult(
            image_bytes=PNG_BYTES,
            content_type="image/png",
            revised_prompt=f"mocked::{prompt}",
        )

    monkeypatch.setattr(
        "app.services.async_image_service.generate_image_with_active_provider",
        fake_generate_image_with_active_provider,
    )

    register_and_login("imageflow")

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Image Flow World",
            "description": "World for image integration tests",
            "short_description": "Image world",
            "is_free_chat_enabled": False,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    character_response = client.post(
        f"/api/v1/worlds/{world_id}/characters/",
        json={
            "name": "Painter Ash",
            "description": "A character used for image generation testing",
        },
    )
    assert character_response.status_code == 201, character_response.text
    character_id = character_response.json()["data"]["id"]

    image_response = client.post(
        "/api/v1/images/",
        json={
            "element_type": "character",
            "element_id": character_id,
            "prompt_override": "Portrait of Painter Ash under golden light",
        },
    )
    assert image_response.status_code == 202, image_response.text
    image_body = image_response.json()
    assert image_body["success"] is True
    job_id = image_body["data"]["job_id"]

    status_payload = None
    for _ in range(20):
        status_response = client.get(f"/api/v1/images/job/{job_id}/status")
        assert status_response.status_code == 200, status_response.text
        status_payload = status_response.json()
        if status_payload["state"] == "COMPLETED":
            break
        time.sleep(0.1)

    assert status_payload is not None
    assert status_payload["state"] == "COMPLETED"
    result_data = status_payload["result"]
    image_id = result_data["image_id"]
    assert result_data["element_type"] == "character"
    assert result_data["element_id"] == character_id
    assert result_data["image_url"]

    images_response = client.get(f"/api/v1/images/character/{character_id}")
    assert images_response.status_code == 200, images_response.text
    images_body = images_response.json()
    assert images_body["success"] is True
    assert images_body["data"][0]["id"] == image_id
    assert images_body["data"][0]["is_current"] is True

    set_current_response = client.post(f"/api/v1/images/character/{character_id}/set-current/{image_id}")
    assert set_current_response.status_code == 200, set_current_response.text
    set_current_body = set_current_response.json()
    assert set_current_body["success"] is True
    assert set_current_body["data"]["image_id"] == image_id

    def fetch_image_state(session):
        async def _inner():
            image = (
                await session.execute(select(GeneratedImage).where(GeneratedImage.id == image_id))
            ).scalar_one()
            job = (
                await session.execute(select(JobStatus).where(JobStatus.job_id == job_id))
            ).scalar_one()
            return {
                "blob_path": image.blob_path,
                "revised_prompt": image.revised_prompt,
                "job_state": job.state,
            }

        return _inner()

    state = run_db(fetch_image_state)
    image_path = app_instance.state.test_storage_root / "uploads" / "generated_images" / state["blob_path"]
    assert state["revised_prompt"].startswith("mocked::Portrait of Painter Ash under golden light")
    assert state["job_state"] == JobStateEnum.COMPLETED
    assert image_path.exists()

    delete_response = client.delete(f"/api/v1/images/{image_id}")
    assert delete_response.status_code == 200, delete_response.text
    delete_body = delete_response.json()
    assert delete_body["success"] is True
    assert delete_body["data"]["deleted_image_id"] == image_id
    assert not image_path.exists()

    def fetch_deleted_image(session):
        async def _inner():
            return (
                await session.execute(select(GeneratedImage).where(GeneratedImage.id == image_id))
            ).scalar_one_or_none()

        return _inner()

    assert run_db(fetch_deleted_image) is None
