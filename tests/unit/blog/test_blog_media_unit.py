"""Mock-based unit tests for the blog_media router."""
import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.routers.blog_media import generate_filename, get_file_type
from app.routers.blog_media import router as blog_media_router

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Pure-function helpers
# ---------------------------------------------------------------------------

def test_get_file_type_image():
    assert get_file_type("image/jpeg") == "image"
    assert get_file_type("image/png") == "image"
    assert get_file_type("image/gif") == "image"
    assert get_file_type("image/webp") == "image"


def test_get_file_type_video():
    assert get_file_type("video/mp4") == "video"
    assert get_file_type("video/webm") == "video"
    assert get_file_type("video/ogg") == "video"


def test_get_file_type_audio():
    assert get_file_type("audio/mp3") == "audio"
    assert get_file_type("audio/wav") == "audio"
    assert get_file_type("audio/ogg") == "audio"


def test_get_file_type_unknown_returns_document():
    assert get_file_type("application/pdf") == "document"
    assert get_file_type("text/plain") == "document"
    assert get_file_type("application/octet-stream") == "document"


def test_generate_filename_includes_user_id_and_extension():
    name = generate_filename("photo.jpg", 7)
    assert name.startswith("7_")
    assert name.endswith(".jpg")


def test_generate_filename_with_suffix():
    name = generate_filename("photo.jpg", 7, "16x9")
    assert name.startswith("7_")
    assert "_16x9" in name
    assert name.endswith(".jpg")


def test_generate_filename_is_unique():
    a = generate_filename("photo.jpg", 1)
    b = generate_filename("photo.jpg", 1)
    assert a != b


def test_generate_filename_lowercases_extension():
    name = generate_filename("PHOTO.JPG", 1)
    assert name.endswith(".jpg")


# ---------------------------------------------------------------------------
# DELETE endpoint: user-scoping and missing-file checks
# ---------------------------------------------------------------------------

def test_delete_rejects_file_owned_by_other_user(unit_client_factory):
    """Requesting deletion of a file whose name doesn't start with the caller's user id returns 403."""
    client = unit_client_factory(blog_media_router)
    # mock_user.id == 1; file belongs to user 2
    resp = client.delete("/api/blog/media/2_someone-elses-file.jpg")
    assert resp.status_code == 403
    assert "own" in resp.json()["detail"].lower()


def test_delete_returns_404_when_file_not_found(unit_client_factory, tmp_path):
    """Requesting deletion of a non-existent user-owned file returns 404."""
    client = unit_client_factory(blog_media_router)
    with patch("app.routers.blog_media.UPLOAD_DIR", new=tmp_path):
        resp = client.delete("/api/blog/media/1_nonexistent.jpg")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /upload: size enforcement
# ---------------------------------------------------------------------------

def test_upload_returns_413_for_oversized_image(unit_client_factory):
    """Uploading an image larger than MAX_IMAGE_SIZE (5 MB) returns 413."""
    client = unit_client_factory(blog_media_router)
    # 6 MB > 5 MB limit; size check happens before PIL validation
    oversized = b"x" * (6 * 1024 * 1024)
    resp = client.post(
        "/api/blog/media/upload",
        files={"file": ("big.jpg", io.BytesIO(oversized), "image/jpeg")},
    )
    assert resp.status_code == 413


# ---------------------------------------------------------------------------
# GET /list: user-scoped empty result
# ---------------------------------------------------------------------------

def test_list_returns_empty_for_user_with_no_files(unit_client_factory, tmp_path):
    """An authenticated user with no uploaded files gets an empty list."""
    client = unit_client_factory(blog_media_router)
    with patch("app.routers.blog_media.UPLOAD_DIR", new=tmp_path):
        resp = client.get("/api/blog/media/list")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


def test_list_only_returns_files_for_current_user(unit_client_factory, tmp_path):
    """Files belonging to other users are excluded from the media list."""
    # Create a file for user 99 (not the current mock_user whose id == 1)
    other_file = tmp_path / "99_other-user-photo.jpg"
    other_file.write_bytes(b"fake-image-data")

    client = unit_client_factory(blog_media_router)
    with patch("app.routers.blog_media.UPLOAD_DIR", new=tmp_path):
        resp = client.get("/api/blog/media/list")
    assert resp.status_code == 200
    items = resp.json()["data"]
    assert not any(item["storage_path"].startswith("99_") for item in items)
