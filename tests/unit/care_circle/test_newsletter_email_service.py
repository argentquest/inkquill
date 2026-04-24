import uuid
from pathlib import Path

from app.services.care_circle import newsletter_email_service as service


def test_prepare_served_images_for_email_uses_public_app_url(monkeypatch):
    monkeypatch.setattr(service.settings, "APP_URL", "https://care-circle.example.com")

    html = '<img src="/api/v1/care-circle/cached-image/20/2026-04-23/example.jpg">'

    result = service._prepare_served_images_for_email(html)

    assert 'src="https://care-circle.example.com/api/v1/care-circle/cached-image/20/2026-04-23/example.jpg"' in result


def test_embed_images_leaves_remote_urls_as_normal_images():
    html = '<img src="https://care-circle.example.com/api/v1/care-circle/cached-image/20/2026-04-23/example.jpg">'

    rewritten_html, image_parts = service._embed_images(html)

    assert rewritten_html == html
    assert image_parts == []


def test_embed_images_still_embeds_true_local_file_paths():
    image_path = Path("artifacts") / f"test_embed_image_{uuid.uuid4().hex}.jpg"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(b"\xff\xd8\xff\xd9")
    html = f'<img src="{image_path.as_posix()}">'

    rewritten_html, image_parts = service._embed_images(html)

    assert "cid:" in rewritten_html
    assert len(image_parts) == 1
