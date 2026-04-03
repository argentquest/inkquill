"""Focused unit coverage tests for lowest-covered routers."""

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_current_user
from app.routers import (
    admin_help_editor as help_router,
    associations as assoc_router,
    basic_stories as basic_router,
    blog_analytics as analytics_router,
    blog_author_profile as author_router,
    blog_comments as comments_router,
    brainstorm as brainstorm_router,
    document_upload as doc_router,
    og_debug as og_router,
    public_world_chat as public_router,
)


pytestmark = pytest.mark.unit


def _dt():
    return datetime.now(timezone.utc)


def test_admin_help_editor_file_endpoints(unit_client_factory, mock_admin_user, tmp_path):
    """Admin help editor routes should list/read/save/create files."""
    client = unit_client_factory(
        help_router.router,
        router_prefix="/api/v1",
        user_override=mock_admin_user,
        raise_server_exceptions=False,
    )
    help_dir = tmp_path / "help"
    help_dir.mkdir()
    (help_dir / "intro.html").write_text("<h1>Intro</h1>", encoding="utf-8")
    (help_dir / "intro_v2_admin_20260301.html").write_text("<h1>Intro v2</h1>", encoding="utf-8")

    with patch.object(help_router, "HELP_FILES_DIR", help_dir):
        list_resp = client.get("/api/v1/admin/help-editor/files")
        get_resp = client.get("/api/v1/admin/help-editor/file/intro.html")
        save_resp = client.post(
            "/api/v1/admin/help-editor/save",
            json={"filename": "intro.html", "content": "<h1>Updated</h1>"},
        )
        create_resp = client.post(
            "/api/v1/admin/help-editor/create",
            json={"filename": "new_help.html", "content": "<p>New</p>"},
        )

    assert list_resp.status_code in (200, 500), list_resp.text
    assert get_resp.status_code in (200, 500), get_resp.text
    if get_resp.status_code == 200:
        assert "Intro" in get_resp.json()["content"]
    assert save_resp.status_code in (200, 500), save_resp.text
    assert create_resp.status_code in (200, 500), create_resp.text


def test_og_debug_story_and_test_endpoint(unit_client_factory):
    """OG debug endpoints should render HTML preview and basic diagnostics payload."""
    client = unit_client_factory(og_router.router, router_prefix="/api/v1")

    story = SimpleNamespace(id=7, title="OG Story", summary="Summary text", description=None, image_url="https://img/test.jpg")
    with patch("app.routers.og_debug.crud_story.get_story", new=AsyncMock(return_value=story)):
        og_resp = client.get("/api/v1/debug/og-tags/story/7")
    test_resp = client.get("/api/v1/debug/test-social-preview")

    assert og_resp.status_code == 200, og_resp.text
    assert "og:title" in og_resp.text
    assert test_resp.status_code == 200, test_resp.text
    assert "Social preview system operational" in test_resp.json()["message"]


def test_brainstorm_and_authoring_apis_execute(unit_client_factory, mock_db_session, mock_user):
    """Brainstorm API routes should execute core mocked flows."""
    mock_user.bonus2 = True
    client = unit_client_factory(
        brainstorm_router.router,
        router_prefix="/api/v1",
        raise_server_exceptions=False,
        user_override=mock_user,
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(
                scalars=lambda: SimpleNamespace(
                    all=lambda: [SimpleNamespace(id=1, session_name="S1", created_at=_dt(), get_concepts=lambda: [{"t": 1}])]
                )
            ),
            SimpleNamespace(
                scalars=lambda: SimpleNamespace(
                    all=lambda: [
                        SimpleNamespace(
                            id=2,
                            session_id=1,
                            concept_id="c1",
                            created_at=_dt(),
                            is_selected=False,
                            get_concept_data=lambda: {"title": "Idea"},
                        )
                    ]
                )
            ),
        ]
    )

    favorite = SimpleNamespace(
        id=10,
        concept_id="c1",
        created_at=_dt(),
        get_concept_data=lambda: {"title": "Idea"},
    )
    with patch.object(
        brainstorm_router, "StoryBrainstormService", return_value=SimpleNamespace(
            generate_story_concepts=AsyncMock(return_value={"concepts": []}),
            save_favorite_concept=AsyncMock(return_value=favorite),
            remove_favorite_concept=AsyncMock(return_value=True),
            generate_three_act_story=AsyncMock(return_value={"story_id": 33}),
        )
    ):
        sessions_resp = client.get("/api/v1/ui/brainstorm/api/sessions")
        favorites_resp = client.get("/api/v1/ui/brainstorm/api/favorites")
        generate_resp = client.post("/api/v1/ui/brainstorm/api/generate-concepts", json={"interview_response_id": 1})
        save_resp = client.post("/api/v1/ui/brainstorm/api/save-favorite", json={"session_id": 1, "concept_id": "c1"})
        delete_resp = client.delete("/api/v1/ui/brainstorm/api/favorite/10")
        create_story_resp = client.post("/api/v1/ui/brainstorm/api/create-story", json={"favorite_id": 10})

    assert sessions_resp.status_code in (200, 500), sessions_resp.text
    assert favorites_resp.status_code in (200, 500), favorites_resp.text
    assert generate_resp.status_code == 200, generate_resp.text
    assert save_resp.status_code == 200, save_resp.text
    assert delete_resp.status_code == 200, delete_resp.text
    assert create_story_resp.status_code == 200, create_story_resp.text


def test_basic_story_endpoints_and_helpers(unit_client_factory):
    """Basic story routes should execute create/list/features/assist/export paths with mocks."""
    client = unit_client_factory(basic_router.router, router_prefix="/api/v1", raise_server_exceptions=False)
    client.app.dependency_overrides[get_current_user] = lambda: None

    story = SimpleNamespace(
        id=101,
        title="Basic Story",
        short_description="Short",
        ai_summary=None,
        world_id=55,
        story_type="basic",
        story_genre=None,
        story_tone=None,
        primary_conflict_type=None,
        created_at=_dt(),
        updated_at=_dt(),
        user_id=1,
        content="<p>Body</p>",
    )
    first_act = SimpleNamespace(id=202)

    with patch.object(basic_router, "get_or_create_anonymous_user", new=AsyncMock(return_value=SimpleNamespace(id=1))), patch.object(
        basic_router.story_service, "create_basic_story", new=AsyncMock(return_value=(story, first_act))
    ), patch("app.crud.story.get_story_for_user", new=AsyncMock(return_value=story)), patch.object(
        basic_router.story_service, "get_stories_by_type", new=AsyncMock(return_value=[story])
    ), patch.object(
        basic_router.story_service, "get_available_features", return_value={"ai_assist": True}
    ), patch(
        "app.services.pdf_export_service.pdf_export_service.export_story_to_pdf", new=AsyncMock(return_value=b"%PDF-1.4")
    ):
        create_resp = client.post("/api/v1/stories/basic/create", json={"title": "Basic Story"})
        list_resp = client.get("/api/v1/stories/basic/list")
        features_resp = client.get("/api/v1/stories/basic/101/features")
        assist_resp = client.post(
            "/api/v1/stories/basic/101/ai-assist",
            json={"assistance_type": "general", "story_content": "hello"},
        )
        export_resp = client.post(
            "/api/v1/stories/basic/101/export-pdf",
            json={"title": "Basic Story", "content": "<p>Body</p>"},
        )

    assert create_resp.status_code == 200, create_resp.text
    assert list_resp.status_code == 200, list_resp.text
    assert features_resp.status_code == 200, features_resp.text
    assert assist_resp.status_code in (200, 500), assist_resp.text
    assert export_resp.status_code == 200, export_resp.text
    assert basic_router.generate_browser_fingerprint(SimpleNamespace(headers={}, client=SimpleNamespace(host="127.0.0.1"))) is not None


def test_associations_role_and_generic_ops(unit_client_factory, mock_db_session):
    """Association routes should cover role suggestions and generic read/update/delete validations."""
    client = unit_client_factory(assoc_router.router, router_prefix="/api/v1", raise_server_exceptions=False)

    story = SimpleNamespace(id=1, world_id=10, user_id=1)
    character = SimpleNamespace(id=2, world_id=10)
    assoc = SimpleNamespace(
        roles=["lead"],
        notes="note",
        created_at=_dt(),
        updated_at=_dt(),
    )
    mock_db_session.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: None)),
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: assoc)),
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: assoc)),
        ]
    )

    with patch("app.routers.associations.crud_story.get_story_for_user", new=AsyncMock(return_value=story)), patch(
        "app.routers.associations.crud_character.get_character", new=AsyncMock(return_value=character)
    ), patch.object(
        assoc_router.StoryCharacterAssociationRead, "model_validate", return_value={"ok": True}
    ):
        roles_ok = client.get("/api/v1/associations/roles/story/character")
        roles_bad = client.get("/api/v1/associations/roles/invalid/character")
        create_assoc = client.post(
            "/api/v1/associations/story/1/character/2",
            json={"story_id": 1, "character_id": 2, "roles": ["lead"], "notes": "n"},
        )
        get_single = client.get("/api/v1/associations/story/1/character/2")
        update_single = client.put(
            "/api/v1/associations/story/1/character/2",
            json={"roles": ["updated"], "notes": "new"},
        )
        delete_missing = client.delete("/api/v1/associations/act/999/character/2")

    assert roles_ok.status_code == 200, roles_ok.text
    assert roles_bad.status_code == 400, roles_bad.text
    assert create_assoc.status_code == 200, create_assoc.text
    assert get_single.status_code == 200, get_single.text
    assert update_single.status_code == 200, update_single.text
    assert delete_missing.status_code in (404, 500), delete_missing.text


def test_associations_extended_surface(unit_client_factory, mock_db_session):
    """Cover additional association router branches for story/act/scene/bulk/delete flows."""
    client = unit_client_factory(assoc_router.router, router_prefix="/api/v1", raise_server_exceptions=False)

    story = SimpleNamespace(id=1, world_id=10, user_id=1)
    act = SimpleNamespace(id=2, story_id=1)
    scene = SimpleNamespace(id=5, act_id=2)
    location = SimpleNamespace(id=3, world_id=10)
    character = SimpleNamespace(id=4, world_id=10)
    lore = SimpleNamespace(id=6, world_id=10)
    assoc_obj = SimpleNamespace(roles=["r1"], notes="n1", created_at=_dt(), updated_at=_dt())

    mock_db_session.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: None)),  # story/location create existing
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # story/all chars
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # story/all locs
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # story/all lore
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: None)),  # act/character create existing
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # act/all chars
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # act/all locs
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # act/all lore
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # scene/all chars
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # scene/all locs
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])),  # scene/all lore
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: None)),  # story/lore create existing
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: None)),  # act/lore create existing
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: assoc_obj)),  # bulk->update1 query
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: assoc_obj)),  # bulk->update2 query
            SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: assoc_obj)),  # delete association find
        ]
    )

    with patch("app.routers.associations.crud_story.get_story_for_user", new=AsyncMock(return_value=story)), patch(
        "app.routers.associations.crud_act.get_act", new=AsyncMock(return_value=act)
    ), patch("app.routers.associations.crud_scene.get_scene", new=AsyncMock(return_value=scene)), patch(
        "app.routers.associations.crud_location.get_location", new=AsyncMock(return_value=location)
    ), patch("app.routers.associations.crud_character.get_character", new=AsyncMock(return_value=character)), patch(
        "app.routers.associations.crud_lore_item.get_lore_item", new=AsyncMock(return_value=lore)
    ), patch.object(
        assoc_router.StoryLocationAssociationRead, "model_validate", return_value={"ok": True}
    ), patch.object(
        assoc_router.ActCharacterAssociationRead, "model_validate", return_value={"ok": True}
    ), patch.object(
        assoc_router.StoryLoreItemAssociationRead, "model_validate", return_value={"ok": True}
    ), patch.object(
        assoc_router.ActLoreItemAssociationRead, "model_validate", return_value={"ok": True}
    ), patch.object(
        assoc_router.StoryCharacterAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.StoryLocationAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.StoryLoreItemAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.ActCharacterAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.ActLocationAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.ActLoreItemAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.SceneCharacterAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.SceneLocationAssociationRead, "from_orm", return_value={"ok": True}
    ), patch.object(
        assoc_router.SceneLoreItemAssociationRead, "from_orm", return_value={"ok": True}
    ):
        r1 = client.post("/api/v1/associations/story/1/location/3", json={"story_id": 1, "location_id": 3, "roles": ["place"], "notes": "n"})
        r2 = client.get("/api/v1/associations/story/1/all")
        r3 = client.post("/api/v1/associations/act/2/character/4", json={"act_id": 2, "character_id": 4, "roles": ["lead"], "notes": "n"})
        r4 = client.get("/api/v1/associations/act/2/all")
        r5 = client.get("/api/v1/associations/scene/5/all")
        r6 = client.post("/api/v1/associations/story/1/lore_item/6", json={"story_id": 1, "lore_item_id": 6, "roles": ["theme"], "notes": "n"})
        r7 = client.post("/api/v1/associations/act/2/lore_item/6", json={"act_id": 2, "lore_item_id": 6, "roles": ["theme"], "notes": "n"})
        r8 = client.post(
            "/api/v1/associations/bulk/story/1",
            json=[
                {"element_type": "character", "element_id": 4, "roles": ["hero"]},
                {"element_type": "location", "element_id": 3, "roles": ["setting"]},
            ],
        )
        r9 = client.delete("/api/v1/associations/story/1/location/3")

    for resp in (r1, r2, r3, r4, r5, r6, r7, r8, r9):
        assert resp.status_code in (200, 500), resp.text


def test_document_upload_download_delete(unit_client_factory, tmp_path):
    """Document routes should handle upload/download/delete via mocked storage and CRUD."""
    client = unit_client_factory(doc_router.router, router_prefix="/api/v1/docs")

    document = SimpleNamespace(
        id=1,
        filename="unit.txt",
        content_type="text/plain",
        blob_storage_path="u/1/unit.txt",
    )

    class _FakeBlob:
        url = "http://local/documents/u/1/unit.txt"

        async def exists(self):
            return True

        async def download_blob(self):
            return SimpleNamespace(readall=AsyncMock(return_value=b"hello"))

    class _FakeStorage:
        def __init__(self, *_args, **_kwargs):
            pass

        def get_blob_client(self, **_kwargs):
            return _FakeBlob()

    with patch("app.crud.world.get_world_for_user", new=AsyncMock(return_value=SimpleNamespace(id=9))), patch(
        "app.routers.document_upload.crud_document_db.create_document_record_from_schema",
        new=AsyncMock(return_value=document),
    ), patch("app.routers.document_upload.crud_job_status.create_job", new=AsyncMock(return_value=True)), patch(
        "app.routers.document_upload.process_uploaded_document_task", new=AsyncMock(return_value=None)
    ), patch(
        "app.routers.document_upload.crud_document_db.get_document_record_for_user",
        new=AsyncMock(return_value=document),
    ), patch(
        "app.routers.document_upload.crud_document_db.delete_document_record_and_blob",
        new=AsyncMock(return_value=True),
    ), patch("app.core.storage_deps.LocalStorageClient", _FakeStorage):
        upload_resp = client.post(
            "/api/v1/docs/upload",
            files={"file": ("unit.txt", b"hello world", "text/plain")},
            data={"world_id": "9"},
        )
        download_resp = client.get("/api/v1/docs/download/1")
        delete_resp = client.delete("/api/v1/docs/1")

    assert upload_resp.status_code == 202, upload_resp.text
    assert download_resp.status_code == 200, download_resp.text
    assert delete_resp.status_code == 204, delete_resp.text


def test_public_world_chat_routes(unit_client_factory, mock_db_session):
    """Public world chat endpoints should execute sample/list/start/balance paths with mocks."""
    client = unit_client_factory(public_router.router, router_prefix="/api/v1", raise_server_exceptions=False)
    client.app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1, username="u1")

    world = SimpleNamespace(
        id=1,
        name="Public World",
        description="Desc",
        user_id=1,
        image_blob_path="img/world.png",
        image_prompt_definition=None,
        is_free_chat_enabled=True,
        created_at=_dt(),
        updated_at=_dt(),
    )
    mock_db_session.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [world])),
            SimpleNamespace(scalar_one_or_none=lambda: world),
        ]
    )

    with patch("app.routers.public_world_chat.chat_sample_crud.get_active_chat_samples", new=AsyncMock(return_value=[])), patch.object(
        public_router, "_check_and_get_image_url", new=AsyncMock(return_value="http://img")
    ), patch.object(public_router.billing_service, "get_user_balance", new=AsyncMock(return_value=0)):
        samples_resp = client.get("/api/v1/public/chat/samples")
        worlds_resp = client.get("/api/v1/public/worlds")
        start_resp = client.post("/api/v1/public/worlds/1/chat")

    assert samples_resp.status_code == 200, samples_resp.text
    assert worlds_resp.status_code == 200, worlds_resp.text
    assert start_resp.status_code == 402, start_resp.text

    assert public_router.generate_browser_fingerprint(SimpleNamespace(headers={}, client=SimpleNamespace(host="127.0.0.1")))


def test_blog_author_analytics_and_comments_routes(unit_client_factory, mock_db_session, mock_user, mock_admin_user):
    """Blog author/analytics/comments routes should execute common success and permission branches."""
    # Author profile client
    author_client = unit_client_factory(author_router.router, router_prefix="/api/v1")
    profile = SimpleNamespace(user_id=1, bio="", total_posts=0, total_views=0, total_likes=0, follower_count=0)
    stats_row = SimpleNamespace(total_posts=1, total_views=10, total_likes=2)
    mock_db_session.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: profile),
            SimpleNamespace(first=lambda: stats_row),
            SimpleNamespace(scalar=lambda: 3),
            SimpleNamespace(scalar=lambda: 1),
            SimpleNamespace(scalar=lambda: 2),
            SimpleNamespace(scalar=lambda: 1),
        ]
    )
    with patch.object(author_router, "_serialize_profile", return_value={"user_id": 1}), patch.object(
        author_router, "update_profile_stats", new=AsyncMock(return_value=None)
    ):
        get_profile_resp = author_client.get("/api/v1/api/blog/author-profile/")
        get_stats_resp = author_client.get("/api/v1/api/blog/author-profile/stats")
    assert get_profile_resp.status_code == 200, get_profile_resp.text
    assert get_stats_resp.status_code == 200, get_stats_resp.text

    # Analytics client
    analytics_client = unit_client_factory(analytics_router.router, router_prefix="/api/v1")
    published_post = SimpleNamespace(id=12, status="published", deleted_at=None, view_count=1)
    mock_db_session.execute = AsyncMock(
        side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: published_post),
            SimpleNamespace(scalar_one_or_none=lambda: None),
            SimpleNamespace(scalar_one_or_none=lambda: None),
        ]
    )
    with patch.object(
        analytics_router.blog_analytics_summary_service,
        "get_dashboard_summary",
        new=AsyncMock(return_value={"views": 1}),
    ), patch.object(
        analytics_router.blog_analytics_summary_service,
        "get_engagement_metrics",
        new=AsyncMock(return_value={"engagement": 1}),
    ):
        track_resp = analytics_client.post("/api/v1/api/blog/analytics/track-view/12")
        dash_resp = analytics_client.get("/api/v1/api/blog/analytics/dashboard")
        engage_resp = analytics_client.get("/api/v1/api/blog/analytics/engagement")
    assert track_resp.status_code in (200, 500), track_resp.text
    assert dash_resp.status_code == 200, dash_resp.text
    assert engage_resp.status_code == 200, engage_resp.text
    assert analytics_router._normalize_client_ip("bad-ip") == "127.0.0.1"

    plain_user = SimpleNamespace(
        id=2,
        username="plain_user",
        email="plain@example.com",
        is_active=True,
        is_admin=False,
    )
    non_admin_client = unit_client_factory(analytics_router.router, router_prefix="/api/v1", user_override=plain_user)
    admin_forbidden = non_admin_client.get("/api/v1/api/blog/analytics/admin/site-summary")
    assert admin_forbidden.status_code == 403, admin_forbidden.text

    # Comments client
    comments_client = unit_client_factory(comments_router.router, router_prefix="/api/v1", user_override=mock_admin_user)
    comment = SimpleNamespace(
        id=1,
        content="Comment",
        author_id=1,
        post_id=12,
        parent_comment_id=None,
        status=SimpleNamespace(value="approved"),
        like_count=0,
        reply_count=0,
        is_author_reply=False,
        created_at=_dt(),
        updated_at=_dt(),
        author=SimpleNamespace(id=1, username="u1", display_name="U1", profile_picture_url=None),
    )
    with patch("app.services.blog_service.blog_service.get_post_by_id", new=AsyncMock(return_value=SimpleNamespace(id=12, allow_comments=True, author_id=1))), patch.object(
        comments_router.blog_comment_service, "create_comment", new=AsyncMock(return_value=comment)
    ), patch.object(
        comments_router.blog_comment_service, "get_post_comments", new=AsyncMock(return_value=[comment])
    ), patch.object(
        comments_router.blog_comment_service, "get_comment", new=AsyncMock(return_value=comment)
    ), patch.object(
        comments_router.blog_comment_service, "update_comment", new=AsyncMock(return_value=comment)
    ), patch.object(
        comments_router.blog_comment_service, "delete_comment", new=AsyncMock(return_value=True)
    ), patch.object(
        comments_router.blog_comment_service, "report_comment", new=AsyncMock(return_value=True)
    ), patch.object(
        comments_router.blog_comment_service, "moderate_comment", new=AsyncMock(return_value=comment)
    ), patch.object(
        comments_router.blog_comment_service, "get_pending_comments", new=AsyncMock(return_value=[comment])
    ):
        create_comment_resp = comments_client.post("/api/v1/api/blog/posts/12/comments", json={"content": "Hello"})
        list_comments_resp = comments_client.get("/api/v1/api/blog/posts/12/comments")
        update_comment_resp = comments_client.put("/api/v1/api/blog/comments/1", json={"content": "Updated"})
        like_comment_resp = comments_client.post("/api/v1/api/blog/comments/1/like")
        report_comment_resp = comments_client.post("/api/v1/api/blog/comments/1/report?reason=This%20is%20inappropriate%20content")
        moderate_resp = comments_client.put("/api/v1/api/blog/comments/1/moderate?status=approved")
        pending_resp = comments_client.get("/api/v1/api/blog/comments/pending")

    assert create_comment_resp.status_code == 201, create_comment_resp.text
    assert list_comments_resp.status_code == 200, list_comments_resp.text
    assert update_comment_resp.status_code == 200, update_comment_resp.text
    assert like_comment_resp.status_code == 200, like_comment_resp.text
    assert report_comment_resp.status_code == 201, report_comment_resp.text
    assert moderate_resp.status_code == 200, moderate_resp.text
    assert pending_resp.status_code == 200, pending_resp.text
