from datetime import date
from io import BytesIO

from PIL import Image

from app.services.care_circle import provider_cache


def test_process_images_resizes_and_recompresses_comic_images(tmp_path, monkeypatch):
    source = BytesIO()
    Image.new("RGBA", (1200, 800), color=(255, 0, 0, 255)).save(source, format="PNG")
    image_bytes = source.getvalue()

    class _Response:
        def raise_for_status(self):
            return None

        @property
        def content(self):
            return image_bytes

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return _Response()

    monkeypatch.setattr(provider_cache.httpx, "Client", _Client)

    result = {
        "data": {
            "image_url": "https://example.com/comic.png",
            "rendered_html": '<img src="https://example.com/comic.png" alt="comic">',
        }
    }

    processed = provider_cache._process_images(
        result,
        tmp_path,
        "comic_wuffle",
        patient_id=20,
        for_date=date(2026, 4, 21),
    )

    cached_path = tmp_path / "comic_wuffle_image.jpg"
    assert cached_path.exists()

    with Image.open(cached_path) as image:
        assert image.width == 600
        assert image.height == 400
        assert image.format == "JPEG"

    assert processed["data"]["image_url"].endswith("/comic_wuffle_image.jpg")
    assert processed["data"]["image_url_remote"] == "https://example.com/comic.png"
    assert "comic_wuffle_image.jpg" in processed["data"]["rendered_html"]


def test_process_images_preserves_non_comic_image_extensions(tmp_path, monkeypatch):
    class _Response:
        def raise_for_status(self):
            return None

        @property
        def content(self):
            return b"fake-image"

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return _Response()

    monkeypatch.setattr(provider_cache.httpx, "Client", _Client)

    result = {
        "data": {
            "image_url": "https://example.com/photo.png",
        }
    }

    processed = provider_cache._process_images(
        result,
        tmp_path,
        "animal_friend",
        patient_id=20,
        for_date=date(2026, 4, 21),
    )

    cached_path = tmp_path / "animal_friend_image.png"
    assert cached_path.exists()
    assert processed["data"]["image_url"].endswith("/animal_friend_image.png")
