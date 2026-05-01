"""Integration tests for the media API contracts used by the Care Circle media library."""
import io
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

pytestmark = pytest.mark.integration


def _make_jpg_bytes(color=(120, 80, 40)):
    image = Image.new("RGB", (16, 16), color)
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


def _make_fresh_client(app_instance):
    return TestClient(app_instance, raise_server_exceptions=True)


def _register(client: TestClient, prefix: str = "media_user") -> dict:
    payload = {
        "username": f"{prefix}_{uuid4().hex[:8]}",
        "email": f"{prefix}_{uuid4().hex[:8]}@example.com",
        "password": "integration-pass-123",
        "display_name": f"{prefix.title()} User",
        "terms_accepted": True,
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    return payload


# ---------------------------------------------------------------------------
# Auth enforcement
# ---------------------------------------------------------------------------

def test_media_list_requires_auth(client):
    """Unauthenticated GET /api/blog/media/list returns 401."""
    resp = client.get("/api/blog/media/list")
    assert resp.status_code in {401, 403}, resp.text


def test_media_upload_requires_auth(client):
    """Unauthenticated POST /api/blog/media/upload returns 401."""
    resp = client.post(
        "/api/blog/media/upload",
        files={"file": ("test.jpg", io.BytesIO(_make_jpg_bytes()), "image/jpeg")},
    )
    assert resp.status_code in {401, 403}, resp.text


# ---------------------------------------------------------------------------
# Upload → list → delete lifecycle
# ---------------------------------------------------------------------------

def test_family_user_can_upload_list_and_delete_media(client, register_and_login, app_instance):
    """A care-circle family user can upload an image, see it in their library, and delete it."""
    register_and_login("cc_media_lifecycle")

    upload_resp = client.post(
        "/api/blog/media/upload",
        files={"file": ("family-photo.jpg", io.BytesIO(_make_jpg_bytes()), "image/jpeg")},
        data={"alt_text": "Family photo", "caption": "Our garden"},
    )
    assert upload_resp.status_code == 200, upload_resp.text
    body = upload_resp.json()
    assert body["success"] is True
    media = body["data"]["media"]
    assert media["file_type"] == "image"
    storage_path = media["storage_path"]

    list_resp = client.get("/api/blog/media/list")
    assert list_resp.status_code == 200, list_resp.text
    items = list_resp.json()["data"]
    assert any(item["storage_path"] == storage_path for item in items)

    del_resp = client.delete(f"/api/blog/media/{storage_path}")
    assert del_resp.status_code == 204, del_resp.text

    list_after = client.get("/api/blog/media/list").json()["data"]
    assert not any(item["storage_path"] == storage_path for item in list_after)


def test_upload_response_includes_aspect_ratio_crops(client, register_and_login):
    """Image uploads automatically generate and return aspect-ratio crop URLs."""
    register_and_login("cc_media_crops")

    upload_resp = client.post(
        "/api/blog/media/upload",
        files={"file": ("landscape.jpg", io.BytesIO(_make_jpg_bytes(color=(40, 80, 120))), "image/jpeg")},
    )
    assert upload_resp.status_code == 200, upload_resp.text
    media = upload_resp.json()["data"]["media"]
    assert "aspect_ratio_urls" in media
    aspect_urls = media["aspect_ratio_urls"]
    assert "16x9" in aspect_urls
    assert "5x4" in aspect_urls
    assert "1x1" in aspect_urls


# ---------------------------------------------------------------------------
# User isolation
# ---------------------------------------------------------------------------

def test_media_list_is_scoped_to_current_user(client, register_and_login):
    """Files uploaded by user A are not visible in user B's media library."""
    register_and_login("cc_isolation_a")
    upload_resp = client.post(
        "/api/blog/media/upload",
        files={"file": ("user-a-photo.jpg", io.BytesIO(_make_jpg_bytes(color=(10, 20, 30))), "image/jpeg")},
    )
    assert upload_resp.status_code == 200
    a_path = upload_resp.json()["data"]["media"]["storage_path"]

    client.cookies.clear()
    register_and_login("cc_isolation_b")

    b_list = client.get("/api/blog/media/list")
    assert b_list.status_code == 200
    b_items = b_list.json()["data"]
    assert not any(item["storage_path"] == a_path for item in b_items)


def test_user_cannot_delete_another_users_media(client, register_and_login):
    """Attempting to delete another user's media file returns 403."""
    register_and_login("cc_del_owner")
    upload_resp = client.post(
        "/api/blog/media/upload",
        files={"file": ("owned-photo.jpg", io.BytesIO(_make_jpg_bytes()), "image/jpeg")},
    )
    assert upload_resp.status_code == 200
    a_path = upload_resp.json()["data"]["media"]["storage_path"]

    client.cookies.clear()
    register_and_login("cc_del_thief")

    del_resp = client.delete(f"/api/blog/media/{a_path}")
    assert del_resp.status_code == 403
