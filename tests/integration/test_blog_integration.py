import pytest
from sqlalchemy import select

from app.models.blog_comment import BlogComment, CommentStatus
from app.models.blog_follow import BlogFollow
from app.models.blog_like import BlogLike
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.user import User


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_blog_category_post_comment_and_engagement_flow(client, register_and_login, run_db):
    admin_credentials, _ = register_and_login("blogadmin")
    author_credentials, _ = register_and_login("blogauthor")
    reader_credentials, _ = register_and_login("blogreader")

    def promote_admin_and_capture_ids(session):
        async def _inner():
            admin = (
                await session.execute(select(User).where(User.username == admin_credentials["username"]))
            ).scalar_one()
            author = (
                await session.execute(select(User).where(User.username == author_credentials["username"]))
            ).scalar_one()
            reader = (
                await session.execute(select(User).where(User.username == reader_credentials["username"]))
            ).scalar_one()
            admin.is_admin = True
            await session.commit()
            return {"admin_id": admin.id, "author_id": author.id, "reader_id": reader.id}

        return _inner()

    ids = run_db(promote_admin_and_capture_ids)

    admin_headers = {
        "Authorization": f"Bearer {_get_access_token(client, admin_credentials['username'], admin_credentials['password'])}"
    }
    author_headers = {
        "Authorization": f"Bearer {_get_access_token(client, author_credentials['username'], author_credentials['password'])}"
    }
    reader_headers = {
        "Authorization": f"Bearer {_get_access_token(client, reader_credentials['username'], reader_credentials['password'])}"
    }

    create_category_response = client.post(
        "/api/blog/categories/",
        json={
            "name": "Integration Blog",
            "slug": "integration-blog",
            "description": "Blog category for integration coverage",
            "color": "#112233",
            "icon": "pencil",
            "display_order": 1,
            "is_active": True,
        },
        headers=admin_headers,
    )
    assert create_category_response.status_code == 201, create_category_response.text
    create_category_body = create_category_response.json()
    assert create_category_body["success"] is True
    category_id = create_category_body["data"]["id"]

    list_categories_response = client.get("/api/blog/categories/")
    assert list_categories_response.status_code == 200, list_categories_response.text
    list_categories_body = list_categories_response.json()
    assert list_categories_body["success"] is True
    assert any(category["id"] == category_id for category in list_categories_body["data"])

    create_post_response = client.post(
        "/api/blog/posts",
        json={
            "title": "Integration Blog Post",
            "content": "This is the blog post body used for integration testing.",
            "excerpt": "Integration excerpt",
            "category_id": category_id,
            "allow_comments": True,
            "tags": ["integration", "backend"],
        },
        headers=author_headers,
    )
    assert create_post_response.status_code == 201, create_post_response.text
    create_post_body = create_post_response.json()
    assert create_post_body["success"] is True
    post_id = create_post_body["data"]["id"]
    slug = create_post_body["data"]["slug"]
    assert create_post_body["data"]["status"] == "draft"

    my_posts_response = client.get("/api/blog/my-posts", headers=author_headers)
    assert my_posts_response.status_code == 200, my_posts_response.text
    my_posts_body = my_posts_response.json()
    assert my_posts_body["success"] is True
    assert any(post["id"] == post_id for post in my_posts_body["data"])

    update_post_response = client.put(
        f"/api/blog/posts/{post_id}",
        json={
            "title": "Integration Blog Post Updated",
            "excerpt": "Updated excerpt",
            "tags": ["integration", "react"],
        },
        headers=author_headers,
    )
    assert update_post_response.status_code == 200, update_post_response.text
    update_post_body = update_post_response.json()
    assert update_post_body["success"] is True
    assert update_post_body["data"]["title"] == "Integration Blog Post Updated"
    slug = update_post_body["data"]["slug"]

    publish_post_response = client.post(f"/api/blog/posts/{post_id}/publish", headers=author_headers)
    assert publish_post_response.status_code == 200, publish_post_response.text
    publish_post_body = publish_post_response.json()
    assert publish_post_body["success"] is True
    assert publish_post_body["data"]["status"] == "published"

    list_posts_response = client.get("/api/blog/posts")
    assert list_posts_response.status_code == 200, list_posts_response.text
    list_posts_body = list_posts_response.json()
    assert list_posts_body["success"] is True
    assert any(post["id"] == post_id for post in list_posts_body["data"])

    get_post_response = client.get(f"/api/blog/posts/{slug}", headers=reader_headers)
    assert get_post_response.status_code == 200, get_post_response.text
    get_post_body = get_post_response.json()
    assert get_post_body["success"] is True
    assert get_post_body["data"]["slug"] == slug
    assert get_post_body["data"]["view_count"] >= 1

    create_comment_response = client.post(
        f"/api/blog/posts/{post_id}/comments",
        json={"content": "Reader comment on the integration blog post"},
        headers=reader_headers,
    )
    assert create_comment_response.status_code == 201, create_comment_response.text
    create_comment_body = create_comment_response.json()
    assert create_comment_body["success"] is True
    comment_id = create_comment_body["data"]["id"]

    reply_comment_response = client.post(
        f"/api/blog/posts/{post_id}/comments",
        json={
            "content": "Author reply to the reader comment",
            "parent_comment_id": comment_id,
        },
        headers=author_headers,
    )
    assert reply_comment_response.status_code == 201, reply_comment_response.text
    reply_comment_body = reply_comment_response.json()
    assert reply_comment_body["success"] is True
    reply_comment_id = reply_comment_body["data"]["id"]

    get_comments_response = client.get(f"/api/blog/posts/{post_id}/comments")
    assert get_comments_response.status_code == 200, get_comments_response.text
    get_comments_body = get_comments_response.json()
    assert get_comments_body["success"] is True
    assert len(get_comments_body["data"]) == 1
    assert get_comments_body["data"][0]["replies"][0]["id"] == reply_comment_id

    update_comment_response = client.put(
        f"/api/blog/comments/{comment_id}",
        json={"content": "Reader updated comment"},
        headers=reader_headers,
    )
    assert update_comment_response.status_code == 200, update_comment_response.text
    assert update_comment_response.json()["data"]["content"] == "Reader updated comment"

    like_comment_response = client.post(f"/api/blog/comments/{reply_comment_id}/like", headers=reader_headers)
    assert like_comment_response.status_code == 200, like_comment_response.text
    like_comment_body = like_comment_response.json()
    assert like_comment_body["success"] is True
    assert like_comment_body["data"]["like_count"] == 1

    report_comment_response = client.post(
        f"/api/blog/comments/{reply_comment_id}/report",
        params={"reason": "This is a long enough moderation report reason."},
        headers=reader_headers,
    )
    assert report_comment_response.status_code == 201, report_comment_response.text
    assert report_comment_response.json()["success"] is True

    pending_comments_response = client.get("/api/blog/comments/pending", headers=admin_headers)
    assert pending_comments_response.status_code == 200, pending_comments_response.text
    pending_comments_body = pending_comments_response.json()
    assert pending_comments_body["success"] is True
    assert any(comment["id"] == reply_comment_id for comment in pending_comments_body["data"])

    moderate_comment_response = client.put(
        f"/api/blog/comments/{reply_comment_id}/moderate",
        params={"status": "approved", "reason": "Looks fine after review"},
        headers=admin_headers,
    )
    assert moderate_comment_response.status_code == 200, moderate_comment_response.text
    assert moderate_comment_response.json()["data"]["status"] == "approved"

    like_post_response = client.post(f"/api/blog/engagement/posts/{post_id}/like", headers=reader_headers)
    assert like_post_response.status_code == 200, like_post_response.text
    like_post_body = like_post_response.json()
    assert like_post_body["success"] is True
    assert like_post_body["data"]["liked"] is True

    like_status_response = client.get(
        f"/api/blog/engagement/posts/{post_id}/like-status",
        headers=reader_headers,
    )
    assert like_status_response.status_code == 200, like_status_response.text
    assert like_status_response.json()["data"]["liked"] is True

    follow_response = client.post(
        f"/api/blog/engagement/authors/{ids['author_id']}/follow",
        headers=reader_headers,
    )
    assert follow_response.status_code == 200, follow_response.text
    follow_body = follow_response.json()
    assert follow_body["success"] is True
    assert follow_body["data"]["following"] is True

    follow_status_response = client.get(
        f"/api/blog/engagement/authors/{ids['author_id']}/follow-status",
        headers=reader_headers,
    )
    assert follow_status_response.status_code == 200, follow_status_response.text
    assert follow_status_response.json()["data"]["following"] is True

    liked_posts_response = client.get("/api/blog/engagement/my-liked-posts", headers=reader_headers)
    assert liked_posts_response.status_code == 200, liked_posts_response.text
    liked_posts_body = liked_posts_response.json()
    assert liked_posts_body["success"] is True
    assert any(post["id"] == post_id for post in liked_posts_body["data"])

    following_posts_response = client.get("/api/blog/engagement/following-posts", headers=reader_headers)
    assert following_posts_response.status_code == 200, following_posts_response.text
    following_posts_body = following_posts_response.json()
    assert following_posts_body["success"] is True
    assert any(post["id"] == post_id for post in following_posts_body["data"])

    followers_response = client.get("/api/blog/engagement/my-followers", headers=author_headers)
    assert followers_response.status_code == 200, followers_response.text
    followers_body = followers_response.json()
    assert followers_body["success"] is True
    assert followers_body["data"]["total_count"] >= 1

    following_response = client.get("/api/blog/engagement/my-following", headers=reader_headers)
    assert following_response.status_code == 200, following_response.text
    following_body = following_response.json()
    assert following_body["success"] is True
    assert following_body["data"]["total_count"] >= 1

    delete_comment_response = client.delete(f"/api/blog/comments/{comment_id}", headers=author_headers)
    assert delete_comment_response.status_code == 204, delete_comment_response.text

    delete_post_response = client.delete(f"/api/blog/posts/{post_id}", headers=author_headers)
    assert delete_post_response.status_code == 204, delete_post_response.text

    delete_category_response = client.delete(f"/api/blog/categories/{category_id}", headers=admin_headers)
    assert delete_category_response.status_code == 204, delete_category_response.text

    def fetch_blog_state(session):
        async def _inner():
            post = await session.get(BlogPost, post_id)
            comment = await session.get(BlogComment, comment_id)
            reply = await session.get(BlogComment, reply_comment_id)
            like = (
                await session.execute(select(BlogLike).where(BlogLike.post_id == post_id))
            ).scalar_one_or_none()
            follow = (
                await session.execute(
                    select(BlogFollow).where(
                        BlogFollow.author_id == ids["author_id"],
                        BlogFollow.follower_id == ids["reader_id"],
                    )
                )
            ).scalar_one_or_none()
            return {
                "post_status": post.status,
                "post_deleted": post.deleted_at is not None,
                "comment_status": comment.status,
                "reply_status": reply.status,
                "like_exists": like is not None,
                "follow_exists": follow is not None,
            }

        return _inner()

    state = run_db(fetch_blog_state)
    assert state["post_status"] == BlogPostStatus.PUBLISHED
    assert state["post_deleted"] is True
    assert state["comment_status"] == CommentStatus.DELETED
    assert state["reply_status"] == CommentStatus.APPROVED
    assert state["like_exists"] is True
    assert state["follow_exists"] is True
