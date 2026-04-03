import pytest
from sqlalchemy import select

from app.models.forum import ForumCategory, ForumPost, ForumSubscription, ForumThread, ForumVote
from app.models.user import User


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_forum_category_thread_post_flow(client, register_and_login, run_db):
    admin_credentials, _ = register_and_login("forumadmin")
    user_credentials, _ = register_and_login("forumuser")

    def promote_admin(session):
        async def _inner():
            admin = (
                await session.execute(select(User).where(User.username == admin_credentials["username"]))
            ).scalar_one()
            user = (
                await session.execute(select(User).where(User.username == user_credentials["username"]))
            ).scalar_one()
            admin.is_admin = True
            await session.commit()
            return {"admin_id": admin.id, "user_id": user.id}

        return _inner()

    user_ids = run_db(promote_admin)

    admin_token = _get_access_token(client, admin_credentials["username"], admin_credentials["password"])
    user_token = _get_access_token(client, user_credentials["username"], user_credentials["password"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    create_category_response = client.post(
        "/api/forum/categories/",
        json={
            "name": "Integration Discussions",
            "description": "Forum category for integration coverage",
            "slug": "integration-discussions",
            "sort_order": 5,
            "icon": "messages",
        },
        headers=admin_headers,
    )
    assert create_category_response.status_code == 201, create_category_response.text
    create_category_body = create_category_response.json()
    assert create_category_body["success"] is True
    category_id = create_category_body["data"]["id"]
    assert create_category_body["data"]["thread_count"] == 0

    list_categories_response = client.get("/api/forum/categories/")
    assert list_categories_response.status_code == 200, list_categories_response.text
    list_categories_body = list_categories_response.json()
    assert list_categories_body["success"] is True
    assert any(category["id"] == category_id for category in list_categories_body["data"])

    get_category_response = client.get(f"/api/forum/categories/{category_id}")
    assert get_category_response.status_code == 200, get_category_response.text
    assert get_category_response.json()["data"]["slug"] == "integration-discussions"

    slug_response = client.get("/api/forum/categories/slug/integration-discussions")
    assert slug_response.status_code == 200, slug_response.text
    assert slug_response.json()["data"]["id"] == category_id

    create_thread_response = client.post(
        "/api/forum/threads/",
        json={
            "title": "Integration Thread",
            "category_id": category_id,
            "initial_post_content": "Initial integration post body",
            "initial_post_content_html": "<p>Initial integration post body</p>",
        },
        headers=user_headers,
    )
    assert create_thread_response.status_code == 201, create_thread_response.text
    create_thread_body = create_thread_response.json()
    assert create_thread_body["success"] is True
    thread_data = create_thread_body["data"]
    thread_id = thread_data["id"]
    first_post_id = thread_data["posts"][0]["id"]
    assert thread_data["post_count"] == 1
    assert thread_data["is_subscribed"] is True

    list_threads_response = client.get(f"/api/forum/threads/?category_id={category_id}")
    assert list_threads_response.status_code == 200, list_threads_response.text
    list_threads_body = list_threads_response.json()
    assert list_threads_body["success"] is True
    assert any(thread["id"] == thread_id for thread in list_threads_body["data"])

    thread_detail_response = client.get(f"/api/forum/threads/{thread_id}", headers=user_headers)
    assert thread_detail_response.status_code == 200, thread_detail_response.text
    thread_detail_body = thread_detail_response.json()
    assert thread_detail_body["success"] is True
    assert thread_detail_body["data"]["view_count"] >= 1
    assert len(thread_detail_body["data"]["posts"]) == 1

    reply_response = client.post(
        "/api/forum/posts/",
        json={
            "content": "Reply body for integration test",
            "content_html": "<p>Reply body for integration test</p>",
            "thread_id": thread_id,
            "parent_post_id": first_post_id,
        },
        headers=admin_headers,
    )
    assert reply_response.status_code == 201, reply_response.text
    reply_body = reply_response.json()
    assert reply_body["success"] is True
    reply_id = reply_body["data"]["id"]
    assert reply_body["data"]["parent_post_id"] == first_post_id

    thread_posts_response = client.get(f"/api/forum/posts/thread/{thread_id}", headers=user_headers)
    assert thread_posts_response.status_code == 200, thread_posts_response.text
    thread_posts_body = thread_posts_response.json()
    assert thread_posts_body["success"] is True
    assert len(thread_posts_body["data"]) == 2
    root_post = next(post for post in thread_posts_body["data"] if post["id"] == first_post_id)
    assert root_post["replies"][0]["id"] == reply_id

    vote_response = client.post(
        f"/api/forum/posts/{reply_id}/vote",
        json={"post_id": reply_id, "vote_type": "upvote"},
        headers=user_headers,
    )
    assert vote_response.status_code == 200, vote_response.text
    vote_body = vote_response.json()
    assert vote_body["success"] is True
    assert vote_body["data"]["score"] == 1
    assert vote_body["data"]["user_vote"] == "upvote"

    update_post_response = client.put(
        f"/api/forum/posts/{reply_id}",
        json={"content": "Updated reply body"},
        headers=admin_headers,
    )
    assert update_post_response.status_code == 200, update_post_response.text
    update_post_body = update_post_response.json()
    assert update_post_body["success"] is True
    assert update_post_body["data"]["content"] == "Updated reply body"
    assert update_post_body["data"]["edit_count"] == 1

    user_posts_response = client.get(f"/api/forum/posts/user/{user_ids['admin_id']}")
    assert user_posts_response.status_code == 200, user_posts_response.text
    user_posts_body = user_posts_response.json()
    assert user_posts_body["success"] is True
    assert any(post["id"] == reply_id for post in user_posts_body["data"])

    user_stats_response = client.get(f"/api/forum/posts/user/{user_ids['admin_id']}/stats")
    assert user_stats_response.status_code == 200, user_stats_response.text
    user_stats_body = user_stats_response.json()
    assert user_stats_body["success"] is True
    assert user_stats_body["data"]["post_count"] >= 1

    update_thread_response = client.put(
        f"/api/forum/threads/{thread_id}",
        json={"title": "Integration Thread Updated"},
        headers=user_headers,
    )
    assert update_thread_response.status_code == 200, update_thread_response.text
    update_thread_body = update_thread_response.json()
    assert update_thread_body["success"] is True
    assert update_thread_body["data"]["title"] == "Integration Thread Updated"

    subscription_response = client.post(
        f"/api/forum/threads/{thread_id}/subscribe",
        headers=user_headers,
    )
    assert subscription_response.status_code == 200, subscription_response.text
    subscription_body = subscription_response.json()
    assert subscription_body["success"] is True
    assert subscription_body["data"]["subscribed"] is False

    pin_response = client.post(f"/api/forum/threads/{thread_id}/toggle-pin", headers=admin_headers)
    assert pin_response.status_code == 200, pin_response.text
    assert pin_response.json()["data"]["is_pinned"] is True

    lock_response = client.post(f"/api/forum/threads/{thread_id}/toggle-lock", headers=admin_headers)
    assert lock_response.status_code == 200, lock_response.text
    assert lock_response.json()["data"]["is_locked"] is True

    locked_post_attempt = client.post(
        "/api/forum/posts/",
        json={
            "content": "This should fail",
            "thread_id": thread_id,
        },
        headers=user_headers,
    )
    assert locked_post_attempt.status_code == 400, locked_post_attempt.text

    delete_post_response = client.delete(
        f"/api/forum/posts/{reply_id}",
        headers=admin_headers,
        params={"deletion_reason": "integration cleanup"},
    )
    assert delete_post_response.status_code == 204, delete_post_response.text

    delete_thread_response = client.delete(f"/api/forum/threads/{thread_id}", headers=user_headers)
    assert delete_thread_response.status_code == 204, delete_thread_response.text

    update_category_response = client.put(
        f"/api/forum/categories/{category_id}",
        json={"description": "Updated forum category description"},
        headers=admin_headers,
    )
    assert update_category_response.status_code == 200, update_category_response.text
    assert update_category_response.json()["data"]["description"] == "Updated forum category description"

    def fetch_forum_state(session):
        async def _inner():
            deleted_thread = await session.get(ForumThread, thread_id)
            deleted_post = await session.get(ForumPost, reply_id)
            vote = (
                await session.execute(select(ForumVote).where(ForumVote.post_id == reply_id))
            ).scalar_one_or_none()
            subscription = (
                await session.execute(
                    select(ForumSubscription).where(ForumSubscription.thread_id == thread_id)
                )
            ).scalar_one_or_none()
            deleted_category = (
                await session.execute(select(ForumCategory).where(ForumCategory.id == category_id))
            ).scalar_one_or_none()
            return {
                "thread_deleted": deleted_thread.is_deleted,
                "post_deleted": deleted_post.is_deleted,
                "vote_score": deleted_post.score,
                "vote_exists": vote is not None,
                "subscription_exists": subscription is not None,
                "category_exists": deleted_category is not None,
            }

        return _inner()

    state = run_db(fetch_forum_state)
    assert state["thread_deleted"] is True
    assert state["post_deleted"] is True
    assert state["vote_score"] == 1
    assert state["vote_exists"] is True
    assert state["subscription_exists"] is False
    assert state["category_exists"] is True

    delete_category_response = client.delete(f"/api/forum/categories/{category_id}", headers=admin_headers)
    assert delete_category_response.status_code == 204, delete_category_response.text

    def category_missing(session):
        async def _inner():
            deleted_category = (
                await session.execute(select(ForumCategory).where(ForumCategory.id == category_id))
            ).scalar_one_or_none()
            return deleted_category is None

        return _inner()

    assert run_db(category_missing) is True
