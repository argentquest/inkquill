import pytest
from sqlalchemy import select

from app.models.blog_subscription import BlogSubscription, SubscriptionStatus
from app.models.user import User


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_blog_author_profile_tags_subscriptions_search_seo_and_analytics(
    client,
    register_and_login,
    run_db,
):
    admin_credentials, _ = register_and_login("blogextadmin")
    author_credentials, _ = register_and_login("blogextauthor")
    reader_credentials, _ = register_and_login("blogextreader")

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
            "name": "Extended Blog Category",
            "slug": "extended-blog-category",
            "description": "Category for extended backend coverage",
            "color": "#223344",
            "icon": "book",
            "display_order": 2,
            "is_active": True,
        },
        headers=admin_headers,
    )
    assert create_category_response.status_code == 201, create_category_response.text
    category_id = create_category_response.json()["data"]["id"]

    create_primary_post_response = client.post(
        "/api/blog/posts",
        json={
            "title": "Extended Integration Search Post",
            "content": "Extended integration content for analytics, search, and SEO coverage.",
            "excerpt": "Extended integration excerpt for SEO testing.",
            "category_id": category_id,
            "meta_title": "Extended Integration Meta Title",
            "meta_description": "Extended integration meta description that is long enough for SEO endpoint checks.",
            "allow_comments": True,
            "featured_image_url": "https://example.com/feature.jpg",
            "tags": ["extended", "analytics", "search"],
        },
        headers=author_headers,
    )
    assert create_primary_post_response.status_code == 201, create_primary_post_response.text
    primary_post_body = create_primary_post_response.json()
    primary_post_id = primary_post_body["data"]["id"]
    primary_slug = primary_post_body["data"]["slug"]

    create_related_post_response = client.post(
        "/api/blog/posts",
        json={
            "title": "Extended Related Post",
            "content": "Related post content for related-post coverage.",
            "excerpt": "Related excerpt",
            "category_id": category_id,
            "allow_comments": True,
            "tags": ["extended", "related"],
        },
        headers=author_headers,
    )
    assert create_related_post_response.status_code == 201, create_related_post_response.text
    related_post_id = create_related_post_response.json()["data"]["id"]

    assert client.post(f"/api/blog/posts/{primary_post_id}/publish", headers=author_headers).status_code == 200
    assert client.post(f"/api/blog/posts/{related_post_id}/publish", headers=author_headers).status_code == 200

    follow_response = client.post(
        f"/api/blog/engagement/authors/{ids['author_id']}/follow",
        headers=reader_headers,
    )
    assert follow_response.status_code == 200, follow_response.text

    author_profile_response = client.get("/api/blog/author-profile/", headers=author_headers)
    assert author_profile_response.status_code == 200, author_profile_response.text
    author_profile_body = author_profile_response.json()
    assert author_profile_body["success"] is True
    assert author_profile_body["data"]["user_id"] == ids["author_id"]

    update_author_profile_response = client.put(
        "/api/blog/author-profile/",
        json={
            "bio": "Author profile used for extended integration tests.",
            "website_url": "https://example.com/author",
            "twitter_handle": "extendedauthor",
            "allow_comments_default": True,
            "auto_publish": False,
            "email_notifications": True,
        },
        headers=author_headers,
    )
    assert update_author_profile_response.status_code == 200, update_author_profile_response.text
    assert update_author_profile_response.json()["data"]["bio"] == "Author profile used for extended integration tests."

    author_stats_response = client.get("/api/blog/author-profile/stats", headers=author_headers)
    assert author_stats_response.status_code == 200, author_stats_response.text
    author_stats_body = author_stats_response.json()
    assert author_stats_body["success"] is True
    assert author_stats_body["data"]["total_posts"] >= 2
    assert author_stats_body["data"]["follower_count"] >= 1

    author_dashboard_response = client.get("/api/blog/author-profile/dashboard", headers=author_headers)
    assert author_dashboard_response.status_code == 200, author_dashboard_response.text
    author_dashboard_body = author_dashboard_response.json()
    assert author_dashboard_body["success"] is True
    assert author_dashboard_body["data"]["profile"]["total_posts"] >= 2

    public_profile_response = client.get(f"/api/blog/author-profile/{ids['author_id']}")
    assert public_profile_response.status_code == 200, public_profile_response.text
    public_profile_body = public_profile_response.json()
    assert public_profile_body["success"] is True
    assert public_profile_body["data"]["user_id"] == ids["author_id"]

    tag_list_response = client.get("/api/blog/tags/")
    assert tag_list_response.status_code == 200, tag_list_response.text
    tag_list_body = tag_list_response.json()
    assert tag_list_body["success"] is True
    assert any(tag["slug"] == "extended" for tag in tag_list_body["data"])

    popular_tags_response = client.get("/api/blog/tags/popular")
    assert popular_tags_response.status_code == 200, popular_tags_response.text
    assert popular_tags_response.json()["success"] is True

    search_tags_response = client.get("/api/blog/tags/search", params={"q": "ext"})
    assert search_tags_response.status_code == 200, search_tags_response.text
    search_tags_body = search_tags_response.json()
    assert search_tags_body["success"] is True
    assert any(tag["slug"] == "extended" for tag in search_tags_body["data"])

    single_tag_response = client.get("/api/blog/tags/extended")
    assert single_tag_response.status_code == 200, single_tag_response.text
    assert single_tag_response.json()["data"]["slug"] == "extended"

    subscribe_response = client.post(
        "/api/blog/subscriptions/subscribe",
        json={
            "email": reader_credentials["email"],
            "frequency": "weekly",
            "source": "integration-test",
        },
        headers=reader_headers,
    )
    assert subscribe_response.status_code == 201, subscribe_response.text
    subscribe_body = subscribe_response.json()
    assert subscribe_body["success"] is True
    assert subscribe_body["data"]["subscription"]["needs_confirmation"] is True

    def fetch_subscription_tokens(session):
        async def _inner():
            subscription = (
                await session.execute(
                    select(BlogSubscription).where(BlogSubscription.email == reader_credentials["email"].lower())
                )
            ).scalar_one()
            return {
                "confirmation_token": subscription.confirmation_token,
                "unsubscribe_token": subscription.unsubscribe_token,
            }

        return _inner()

    tokens = run_db(fetch_subscription_tokens)

    confirm_response = client.get(f"/api/blog/subscriptions/confirm/{tokens['confirmation_token']}")
    assert confirm_response.status_code == 200, confirm_response.text
    assert "Subscription Confirmed" in confirm_response.text

    my_subscription_response = client.get("/api/blog/subscriptions/my-subscription", headers=reader_headers)
    assert my_subscription_response.status_code == 200, my_subscription_response.text
    my_subscription_body = my_subscription_response.json()
    assert my_subscription_body["success"] is True
    assert my_subscription_body["data"]["subscribed"] is True
    assert my_subscription_body["data"]["subscription"]["status"] == "active"

    update_subscription_response = client.put(
        "/api/blog/subscriptions/my-subscription",
        json={"frequency": "daily", "include_categories": [category_id], "include_tags": [1]},
        headers=reader_headers,
    )
    assert update_subscription_response.status_code == 200, update_subscription_response.text
    update_subscription_body = update_subscription_response.json()
    assert update_subscription_body["success"] is True
    assert update_subscription_body["data"]["subscription"]["frequency"] == "daily"
    assert category_id in update_subscription_body["data"]["subscription"]["include_categories"]

    subscription_stats_response = client.get("/api/blog/subscriptions/stats", headers=admin_headers)
    assert subscription_stats_response.status_code == 200, subscription_stats_response.text
    subscription_stats_body = subscription_stats_response.json()
    assert subscription_stats_body["success"] is True
    assert subscription_stats_body["data"]["active_subscriptions"] >= 1

    subscription_list_response = client.get("/api/blog/subscriptions/list", headers=admin_headers)
    assert subscription_list_response.status_code == 200, subscription_list_response.text
    subscription_list_body = subscription_list_response.json()
    assert subscription_list_body["success"] is True
    assert any(item["email"] == reader_credentials["email"].lower() for item in subscription_list_body["data"])

    search_posts_response = client.get("/api/blog/search/", params={"q": "Extended"})
    assert search_posts_response.status_code == 200, search_posts_response.text
    search_posts_body = search_posts_response.json()
    assert search_posts_body["success"] is True
    assert any(post["id"] == primary_post_id for post in search_posts_body["data"])

    search_suggestions_response = client.get("/api/blog/search/suggestions", params={"q": "Ext"})
    assert search_suggestions_response.status_code == 200, search_suggestions_response.text
    search_suggestions_body = search_suggestions_response.json()
    assert search_suggestions_body["success"] is True
    assert any("Extended" in title for title in search_suggestions_body["data"]["titles"])

    related_posts_response = client.get(f"/api/blog/search/related/{primary_post_id}")
    assert related_posts_response.status_code == 200, related_posts_response.text
    related_posts_body = related_posts_response.json()
    assert related_posts_body["success"] is True
    assert any(post["id"] == related_post_id for post in related_posts_body["data"])

    trending_posts_response = client.get("/api/blog/search/trending")
    assert trending_posts_response.status_code == 200, trending_posts_response.text
    assert trending_posts_response.json()["success"] is True

    seo_analyze_response = client.get(f"/api/blog/seo/analyze/{primary_post_id}", headers=author_headers)
    assert seo_analyze_response.status_code == 200, seo_analyze_response.text
    seo_analyze_body = seo_analyze_response.json()
    assert seo_analyze_body["success"] is True
    assert seo_analyze_body["data"]["post"]["id"] == primary_post_id

    seo_meta_response = client.post(f"/api/blog/seo/generate-meta/{primary_post_id}", headers=author_headers)
    assert seo_meta_response.status_code == 200, seo_meta_response.text
    seo_meta_body = seo_meta_response.json()
    assert seo_meta_body["success"] is True
    assert "suggestions" in seo_meta_body["data"]

    social_preview_response = client.get(
        f"/api/blog/seo/social-preview/{primary_post_id}",
        params={"platform": "twitter"},
    )
    assert social_preview_response.status_code == 200, social_preview_response.text
    social_preview_body = social_preview_response.json()
    assert social_preview_body["success"] is True
    assert social_preview_body["data"]["platform"] == "twitter"

    sharing_stats_response = client.get(
        f"/api/blog/seo/sharing-stats/{primary_post_id}",
        headers=author_headers,
    )
    assert sharing_stats_response.status_code == 200, sharing_stats_response.text
    sharing_stats_body = sharing_stats_response.json()
    assert sharing_stats_body["success"] is True
    assert sharing_stats_body["data"]["post"]["id"] == primary_post_id

    track_view_response = client.post(
        f"/api/blog/analytics/track-view/{primary_post_id}",
        headers=reader_headers,
    )
    assert track_view_response.status_code == 200, track_view_response.text
    track_view_body = track_view_response.json()
    assert track_view_body["success"] is True
    assert track_view_body["data"]["tracked"] is True

    track_read_time_response = client.put(
        f"/api/blog/analytics/track-read-time/{primary_post_id}",
        params={"read_time": 45},
        headers=reader_headers,
    )
    assert track_read_time_response.status_code == 200, track_read_time_response.text
    assert track_read_time_response.json()["success"] is True

    post_analytics_response = client.get(
        f"/api/blog/analytics/post/{primary_post_id}",
        headers=author_headers,
    )
    assert post_analytics_response.status_code == 200, post_analytics_response.text
    post_analytics_body = post_analytics_response.json()
    assert post_analytics_body["success"] is True
    assert post_analytics_body["data"]["post"]["id"] == primary_post_id

    author_overview_response = client.get("/api/blog/analytics/author-overview", headers=author_headers)
    assert author_overview_response.status_code == 200, author_overview_response.text
    author_overview_body = author_overview_response.json()
    assert author_overview_body["success"] is True
    assert author_overview_body["data"]["overview"]["total_posts"] >= 2

    analytics_dashboard_response = client.get("/api/blog/analytics/dashboard", headers=author_headers)
    assert analytics_dashboard_response.status_code == 200, analytics_dashboard_response.text
    analytics_dashboard_body = analytics_dashboard_response.json()
    assert analytics_dashboard_body["success"] is True
    assert "posts" in analytics_dashboard_body["data"]

    analytics_engagement_response = client.get("/api/blog/analytics/engagement", headers=author_headers)
    assert analytics_engagement_response.status_code == 200, analytics_engagement_response.text
    analytics_engagement_body = analytics_engagement_response.json()
    assert analytics_engagement_body["success"] is True
    assert analytics_engagement_body["data"]["total_posts"] >= 2

    analytics_trending_response = client.get("/api/blog/analytics/trending")
    assert analytics_trending_response.status_code == 200, analytics_trending_response.text
    analytics_trending_body = analytics_trending_response.json()
    assert analytics_trending_body["success"] is True

    generate_summary_response = client.post(
        f"/api/blog/analytics/generate-summary/{primary_post_id}",
        headers=author_headers,
    )
    assert generate_summary_response.status_code == 200, generate_summary_response.text
    generate_summary_body = generate_summary_response.json()
    assert generate_summary_body["success"] is True
    assert generate_summary_body["data"]["summary_generated"] is True

    admin_site_summary_response = client.get("/api/blog/analytics/admin/site-summary", headers=admin_headers)
    assert admin_site_summary_response.status_code == 200, admin_site_summary_response.text
    admin_site_summary_body = admin_site_summary_response.json()
    assert admin_site_summary_body["success"] is True
    assert "subscriptions" in admin_site_summary_body["data"]

    unsubscribe_response = client.delete("/api/blog/subscriptions/my-subscription", headers=reader_headers)
    assert unsubscribe_response.status_code == 204, unsubscribe_response.text

    def fetch_subscription_state(session):
        async def _inner():
            subscription = (
                await session.execute(
                    select(BlogSubscription).where(BlogSubscription.email == reader_credentials["email"].lower())
                )
            ).scalar_one()
            return subscription.status

        return _inner()

    subscription_status = run_db(fetch_subscription_state)
    assert subscription_status == SubscriptionStatus.UNSUBSCRIBED
