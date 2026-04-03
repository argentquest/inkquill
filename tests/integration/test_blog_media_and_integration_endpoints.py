import io
from pathlib import Path

import pytest
from PIL import Image
from sqlalchemy import select

from app.models.blog_post_association import BlogPostAssociation


pytestmark = pytest.mark.integration


def _make_png_bytes(color=(20, 40, 60)):
    image = Image.new("RGB", (32, 24), color)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_blog_media_endpoints_use_local_storage_and_cleanup(client, register_and_login):
    register_and_login("blogmediaflow")

    upload_response = client.post(
        "/api/blog/media/upload",
        files={
            "file": ("cover.png", _make_png_bytes(), "image/png"),
        },
        data={"alt_text": "Cover image", "caption": "Primary caption"},
    )
    assert upload_response.status_code == 200, upload_response.text
    upload_body = upload_response.json()
    assert upload_body["success"] is True
    media = upload_body["data"]["media"]
    storage_path = media["storage_path"]

    storage_root = client.app.state.test_storage_root / "uploads" / "blog_media"
    stored_file = storage_root / Path(storage_path)
    assert stored_file.exists()

    list_response = client.get("/api/blog/media/list")
    assert list_response.status_code == 200, list_response.text
    list_body = list_response.json()
    assert list_body["success"] is True
    assert any(item["storage_path"] == storage_path for item in list_body["data"])

    info_response = client.get(f"/api/blog/media/info/{storage_path}")
    assert info_response.status_code == 200, info_response.text
    info_body = info_response.json()
    assert info_body["success"] is True
    assert info_body["data"]["storage_path"] == storage_path
    assert info_body["data"]["width"] == 32
    assert info_body["data"]["height"] == 24

    bulk_response = client.post(
        "/api/blog/media/bulk-upload",
        files=[
            ("files", ("notes-one.txt", b"bulk upload one", "text/plain")),
            ("files", ("notes-two.txt", b"bulk upload two", "text/plain")),
        ],
    )
    assert bulk_response.status_code == 200, bulk_response.text
    bulk_body = bulk_response.json()
    assert bulk_body["success"] is True
    assert len(bulk_body["data"]) == 2
    assert all(item["status"] == "success" for item in bulk_body["data"])

    delete_response = client.delete(f"/api/blog/media/{storage_path}")
    assert delete_response.status_code == 204, delete_response.text
    assert not stored_file.exists()


def test_blog_integration_endpoints_link_storytelling_content(client, register_and_login, run_db):
    register_and_login("blogintegrationflow")

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Integrated Blog World",
            "description": "World used for blog integration tests",
            "short_description": "Integration world",
            "is_free_chat_enabled": False,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Integrated Blog Story",
            "short_description": "Story linked from blog",
            "world_id": world_id,
            "story_type": "advanced",
        },
    )
    assert story_response.status_code == 201, story_response.text
    story_id = story_response.json()["data"]["id"]

    character_response = client.post(
        f"/api/v1/worlds/{world_id}/characters/",
        json={
            "name": "Mira Vale",
            "description": "Navigator tied to blog content",
            "profession": "Navigator",
        },
    )
    assert character_response.status_code == 201, character_response.text
    character_id = character_response.json()["data"]["id"]

    location_response = client.post(
        f"/api/v1/worlds/{world_id}/locations/",
        json={
            "name": "Lantern Harbor",
            "description": "Harbor location tied to blog content",
            "scale": "CITY",
        },
    )
    assert location_response.status_code == 201, location_response.text
    location_id = location_response.json()["data"]["id"]

    lore_response = client.post(
        f"/api/v1/worlds/{world_id}/lore-items/",
        json={
            "title": "Moonwake Charter",
            "description": "Lore item tied to blog content",
            "category": "ARTIFACT",
        },
    )
    assert lore_response.status_code == 201, lore_response.text
    lore_item_id = lore_response.json()["data"]["id"]

    blog_post_response = client.post(
        "/api/blog/posts",
        json={
            "title": "Integrated Blog Post",
            "content": "Blog content linking to world elements.",
            "excerpt": "Integration excerpt",
            "tags": ["integration", "world"],
        },
    )
    assert blog_post_response.status_code == 201, blog_post_response.text
    blog_post_id = blog_post_response.json()["data"]["id"]

    user_content_response = client.get("/api/blog/integration/user-content")
    assert user_content_response.status_code == 200, user_content_response.text
    user_content_body = user_content_response.json()
    assert user_content_body["success"] is True
    assert any(item["id"] == story_id for item in user_content_body["data"]["stories"])
    assert any(item["id"] == world_id for item in user_content_body["data"]["worlds"])

    link_story_response = client.post(
        "/api/blog/integration/link-content",
        params={"blog_post_id": blog_post_id, "content_type": "story", "content_id": story_id},
    )
    assert link_story_response.status_code == 200, link_story_response.text
    link_story_body = link_story_response.json()
    assert link_story_body["success"] is True
    story_link_id = link_story_body["data"]["link"]["link_id"]

    link_world_response = client.post(
        "/api/blog/integration/link-content",
        params={"blog_post_id": blog_post_id, "content_type": "world", "content_id": world_id},
    )
    assert link_world_response.status_code == 200, link_world_response.text

    link_character_response = client.post(
        "/api/blog/integration/link-content",
        params={"blog_post_id": blog_post_id, "content_type": "character", "content_id": character_id},
    )
    assert link_character_response.status_code == 200, link_character_response.text

    link_location_response = client.post(
        "/api/blog/integration/link-content",
        params={"blog_post_id": blog_post_id, "content_type": "location", "content_id": location_id},
    )
    assert link_location_response.status_code == 200, link_location_response.text

    link_lore_response = client.post(
        "/api/blog/integration/link-content",
        params={"blog_post_id": blog_post_id, "content_type": "lore_item", "content_id": lore_item_id},
    )
    assert link_lore_response.status_code == 200, link_lore_response.text

    duplicate_link_response = client.post(
        "/api/blog/integration/link-content",
        params={"blog_post_id": blog_post_id, "content_type": "story", "content_id": story_id},
    )
    assert duplicate_link_response.status_code == 200, duplicate_link_response.text
    assert duplicate_link_response.json()["data"]["message"] == "Content already linked to blog post"

    blog_links_response = client.get(f"/api/blog/integration/blog-links/{blog_post_id}")
    assert blog_links_response.status_code == 200, blog_links_response.text
    blog_links_body = blog_links_response.json()
    assert blog_links_body["success"] is True
    assert blog_links_body["data"]["total_links"] == 5
    assert any(item["content_id"] == story_id for item in blog_links_body["data"]["linked_content"]["stories"])
    assert any(item["content_id"] == world_id for item in blog_links_body["data"]["linked_content"]["worlds"])

    content_blogs_response = client.get(f"/api/blog/integration/content-blogs/story/{story_id}")
    assert content_blogs_response.status_code == 200, content_blogs_response.text
    content_blogs_body = content_blogs_response.json()
    assert content_blogs_body["success"] is True
    assert content_blogs_body["data"]["total_posts"] == 1
    assert content_blogs_body["data"]["blog_posts"][0]["post"]["id"] == blog_post_id

    generate_response = client.post(
        "/api/blog/integration/generate-blog-from-content",
        params={"content_type": "world", "content_id": world_id, "blog_style": "guide"},
    )
    assert generate_response.status_code == 200, generate_response.text
    generate_body = generate_response.json()
    assert generate_body["success"] is True
    assert generate_body["data"]["source_content"]["id"] == world_id
    assert generate_body["data"]["blog_suggestion"]["style"] == "guide"

    unlink_response = client.delete(f"/api/blog/integration/unlink-content/{story_link_id}")
    assert unlink_response.status_code == 200, unlink_response.text
    unlink_body = unlink_response.json()
    assert unlink_body["success"] is True
    assert unlink_body["data"]["unlinked"] is True

    def fetch_association_count(session):
        async def _inner():
            result = await session.execute(
                select(BlogPostAssociation).where(BlogPostAssociation.post_id == blog_post_id)
            )
            return len(result.scalars().all())

        return _inner()

    assert run_db(fetch_association_count) == 4
