# tests/test_remaining_apis.py

"""
Tests for remaining API endpoints not covered in other test files.
Covers social features, maintenance, admin features, and other less common endpoints.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from fastapi import FastAPI


class TestSocialSharingAPIs:
    """Test Social Sharing and Preview endpoints"""

    @pytest.mark.asyncio
    async def test_create_shareable_link(self):
        """Test POST /social/share - Create shareable link"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.story.story_crud.get') as mock_get_story, \
             patch('app.services.social_sharing_service.SocialSharingService.create_share_link') as mock_create_share:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock story ownership
            mock_story = Mock()
            mock_story.id = 1
            mock_story.user_id = 1
            mock_story.title = "Test Story"
            mock_get_story.return_value = mock_story

            # Mock share creation
            mock_share = Mock()
            mock_share.share_code = "abc123def"
            mock_share.expires_at = datetime.now() + timedelta(days=7)
            mock_share.share_url = f"https://app.example.com/shared/story/{mock_share.share_code}"
            mock_create_share.return_value = mock_share

            from app.routers.social_sharing import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/social")
            client = TestClient(app)

            share_request = {
                "content_type": "story",
                "content_id": 1,
                "permissions": ["view", "comment"]
            }

            response = client.post("/api/v1/social/share", json=share_request)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "share_url" in data["data"]
            assert mock_share.share_code in data["data"]["share_url"]

    @pytest.mark.asyncio
    async def test_get_social_preview_world(self):
        """Test GET /social-preview/world/{world_id} - Get OG preview for world"""
        with patch('app.services.social_preview_service.SocialPreviewService.get_world_preview') as mock_get_preview:

            mock_preview = Mock()
            mock_preview.title = "Amazing Fantasy World"
            mock_preview.description = "A magical realm full of wonder and adventure"
            mock_preview.image_url = "https://app.example.com/worlds/1/og-image.jpg"
            mock_preview.url = "https://app.example.com/worlds/1"
            mock_get_preview.return_value = mock_preview

            from app.routers.social_preview import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/social-preview")
            client = TestClient(app)

            response = client.get("/api/v1/social-preview/world/1")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["title"] == "Amazing Fantasy World"
            assert "og" in data["data"] or "opengraph" in data["data"]  # Depending on implementation


class TestMaintenanceAdminAPIs:
    """Test Maintenance and Admin endpoints"""

    @pytest.mark.asyncio
    async def test_get_maintenance_status(self):
        """Test GET /maintenance/status - Get maintenance status"""
        with patch('app.crud.maintenance.maintenance_crud.get_current_status') as mock_get_status:

            mock_status = Mock()
            mock_status.is_enabled = False
            mock_status.message = ""
            mock_status.start_time = None
            mock_status.end_time = None
            mock_get_status.return_value = mock_status

            from app.routers.maintenance import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/maintenance")
            client = TestClient(app)

            response = client.get("/api/v1/maintenance/status")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["is_enabled"] is False

    @pytest.mark.asyncio
    async def test_enable_maintenance_mode(self):
        """Test POST /maintenance/enable - Enable maintenance mode (admin)"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.maintenance.maintenance_crud.enable_maintenance') as mock_enable:

            # Mock admin user
            mock_user = Mock()
            mock_user.is_admin = True
            mock_get_user.return_value = mock_user

            mock_enable.return_value = True

            from app.routers.maintenance import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/maintenance")
            client = TestClient(app)

            maintenance_data = {
                "message": "Scheduled maintenance for system updates",
                "duration_hours": 2
            }

            response = client.post("/api/v1/maintenance/enable", json=maintenance_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_create_news_item(self):
        """Test POST /admin/news/ - Create news item (admin)"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.news.news_crud.create_news') as mock_create_news:

            # Mock admin user
            mock_user = Mock()
            mock_user.is_admin = True
            mock_get_user.return_value = mock_user

            # Mock created news
            mock_news = Mock()
            mock_news.id = 1
            mock_news.title = "New Feature Announcement"
            mock_news.content = "We're excited to announce a new AI writing feature..."
            mock_news.published = False
            mock_create_news.return_value = mock_news

            from app.routers.admin_news import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/admin/news")
            client = TestClient(app)

            news_data = {
                "title": "New Feature Announcement",
                "content": "We're excited to announce a new AI writing feature...",
                "category": "features",
                "published": False
            }

            response = client.post("", json=news_data)

            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["data"]["title"] == "New Feature Announcement"


class TestReferralAPIs:
    """Test Referral System endpoints"""

    @pytest.mark.asyncio
    async def test_get_referral_code(self):
        """Test GET /referrals/my-code - Get user's referral code"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.referral.referral_crud.get_or_create_code') as mock_get_code:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_referral_code = Mock()
            mock_referral_code.code = "USER123"
            mock_referral_code.created_at = datetime.now()
            mock_referral_code.usage_count = 5
            mock_get_code.return_value = mock_referral_code

            from app.routers.referrals import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/referrals")
            client = TestClient(app)

            response = client.get("/api/v1/referrals/my-code")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["code"] == "USER123"
            assert data["data"]["usage_count"] == 5

    @pytest.mark.asyncio
    async def test_get_referral_stats(self):
        """Test GET /referrals/stats - Get referral stats"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.referral.referral_crud.get_referral_stats') as mock_get_stats:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_stats = Mock()
            mock_stats.total_referred = 12
            mock_stats.conversions = 8
            mock_stats.credits_earned = 240
            mock_stats.pending_credits = 60
            mock_get_stats.return_value = mock_stats

            from app.routers.referrals import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/referrals")
            client = TestClient(app)

            response = client.get("/api/v1/referrals/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["total_referred"] == 12
            assert data["data"]["conversions"] == 8


class TestInterviewAPIs:
    """Test Interview System endpoints"""

    @pytest.mark.asyncio
    async def test_start_interview(self):
        """Test POST /interview/start - Start interview"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.interview.interview_crud.create_session') as mock_create_session:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_session = Mock()
            mock_session.id = "session_123"
            mock_session.questions = [
                {"id": 1, "question": "What's your writing experience level?", "type": "choice"},
                {"id": 2, "question": "What genres interest you most?", "type": "multiple_choice"}
            ]
            mock_session.current_question_index = 0
            mock_create_session.return_value = mock_session

            from app.routers.interview import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/interview")
            client = TestClient(app)

            start_data = {
                "interview_type": "welcome"
            }

            response = client.post("/api/v1/interview/start", json=start_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["session_id"] == "session_123"
            assert len(data["data"]["questions"]) == 2

    @pytest.mark.asyncio
    async def test_submit_answer(self):
        """Test POST /interview/answer - Submit answer"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.interview.interview_crud.save_answer') as mock_save_answer, \
             patch('app.crud.interview.interview_crud.get_session') as mock_get_session:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock session exists
            mock_session = Mock()
            mock_session.id = "session_123"
            mock_session.status = "active"
            mock_get_session.return_value = mock_session

            mock_save_answer.return_value = True

            from app.routers.interview import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/interview")
            client = TestClient(app)

            answer_data = {
                "session_id": "session_123",
                "question_id": 1,
                "answer": "intermediate"
            }

            response = client.post("/api/v1/interview/answer", json=answer_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestWelcomeInterviewAPIs:
    """Test Welcome Interview endpoints"""

    @pytest.mark.asyncio
    async def test_analyze_welcome_answers(self):
        """Test POST /welcome-interview/analyze - Analyze welcome interview"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.services.welcome_interview_service.WelcomeInterviewService.analyze_results') as mock_analyze:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_results = Mock()
            mock_results.profile_summary = "Creative writer interested in fantasy and sci-fi"
            mock_results.recommended_features = ["AI Story Wizard", "World Builder", "Character Generator"]
            mock_results.bonus_eligible = True
            mock_results.bonus_amount = 500
            mock_analyze.return_value = mock_results

            from app.routers.welcome_interview import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/welcome-interview")
            client = TestClient(app)

            analysis_data = {
                "answers": {
                    "experience": "intermediate",
                    "genres": ["fantasy", "scifi"],
                    "goals": ["write_novel", "world_building"]
                }
            }

            response = client.post("/api/v1/welcome-interview/analyze", json=analysis_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "profile_summary" in data["data"]
            assert data["data"]["bonus_eligible"] is True

    @pytest.mark.asyncio
    async def test_check_bonus_status(self):
        """Test GET /welcome-interview/bonus-status - Check bonus eligibility"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.welcome_bonus.welcome_bonus_crud.get_bonus_status') as mock_get_status:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_status = Mock()
            mock_status.eligible = True
            mock_status.amount = 500
            mock_status.claimed = False
            mock_status.expires_at = datetime.now() + timedelta(days=30)
            mock_get_status.return_value = mock_status

            from app.routers.welcome_interview import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/welcome-interview")
            client = TestClient(app)

            response = client.get("/api/v1/welcome-interview/bonus-status")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["eligible"] is True
            assert data["data"]["amount"] == 500


class TestBrainstormAPI:
    """Test Brainstorm Session endpoints"""

    @pytest.mark.asyncio
    async def test_create_brainstorm_session(self):
        """Test POST /brainstorm/session - Create brainstorm session"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.brainstorm.brainstorm_crud.create_session') as mock_create_session:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_session = Mock()
            mock_session.id = 1
            mock_session.topic = "Plot ideas for mystery novel"
            mock_session.created_at = datetime.now()
            mock_create_session.return_value = mock_session

            from app.routers.brainstorm import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/brainstorm")
            client = TestClient(app)

            session_data = {
                "topic": "Plot ideas for mystery novel",
                "context": {
                    "genre": "mystery",
                    "setting": "small_town",
                    "character_count": 3
                }
            }

            response = client.post("/api/v1/brainstorm/session", json=session_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Plot ideas" in data["data"]["topic"]

    @pytest.mark.asyncio
    async def test_send_brainstorm_message(self):
        """Test POST /brainstorm/{session_id}/message - Send brainstorm message"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.brainstorm.brainstorm_crud.add_message') as mock_add_message, \
             patch('app.crud.brainstorm.brainstorm_crud.get_session') as mock_get_session:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock session exists and is owned by user
            mock_session = Mock()
            mock_session.id = 1
            mock_session.user_id = 1
            mock_get_session.return_value = mock_session

            # Mock AI response
            mock_message = Mock()
            mock_message.id = 1
            mock_message.content = "That's an interesting direction! Here are some plot twists..."
            mock_message.sender = "ai"
            mock_message.created_at = datetime.now()
            mock_add_message.return_value = mock_message

            from app.routers.brainstorm import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/brainstorm")
            client = TestClient(app)

            message_data = {
                "message": "What if the detective discovers that the victim was their long-lost sibling?"
            }

            response = client.post("/api/v1/brainstorm/1/message", json=message_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "plot twists" in data["data"]["content"].lower()


class TestStoryClassAPIs:
    """Test Story Class Management endpoints"""

    @pytest.mark.asyncio
    async def test_list_story_classes(self):
        """Test GET /story-classes/ - List story classes"""
        with patch('app.crud.story_class.story_class_crud.get_all_classes') as mock_get_classes:

            mock_classes = [
                Mock(id=1, name="Short Story", description="50-5000 words"),
                Mock(id=2, name="Novella", description="20,000-40,000 words"),
                Mock(id=3, name="Novel", description="40,000+ words")
            ]
            mock_get_classes.return_value = mock_classes

            from app.routers.story_class import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/story-classes")
            client = TestClient(app)

            response = client.get("")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 3
            assert data["data"][0]["name"] == "Short Story"

    @pytest.mark.asyncio
    async def test_create_story_class_admin(self):
        """Test POST /story-classes/ - Create class (admin only)"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.story_class.story_class_crud.create_class') as mock_create_class:

            # Mock admin user
            mock_user = Mock()
            mock_user.is_admin = True
            mock_get_user.return_value = mock_user

            # Mock created class
            mock_class = Mock()
            mock_class.id = 4
            mock_class.name = "Epic"
            mock_class.description = "Very long story, 500,000+ words"
            mock_create_class.return_value = mock_class

            from app.routers.story_class import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/story-classes")
            client = TestClient(app)

            class_data = {
                "name": "Epic",
                "description": "Very long story, 500,000+ words",
                "word_count_min": 500000,
                "word_count_max": None
            }

            response = client.post("", json=class_data)

            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Epic"


class TestPromptAPIs:
    """Test Prompt Management endpoints"""

    @pytest.mark.asyncio
    async def test_list_prompts(self):
        """Test GET /prompts/ - List prompts"""
        with patch('app.crud.prompt.prompt_crud.get_user_prompts') as mock_get_prompts:
            # This endpoint might be user-specific or public

            mock_prompts = [
                Mock(id=1, title="Action Scene Starter", content="The explosion rocked the building..."),
                Mock(id=2, title="Character Introduction", content="She walked into the room with confidence...")
            ]
            mock_get_prompts.return_value = mock_prompts

            from app.routers.prompt import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/prompts")
            client = TestClient(app)

            response = client.get("")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_create_prompt(self):
        """Test POST /prompts/ - Create prompt"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.prompt.prompt_crud.create_prompt') as mock_create_prompt:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_prompt = Mock()
            mock_prompt.id = 3
            mock_prompt.title = "Mystery Plot Hook"
            mock_prompt.content = "The old clock struck midnight as the detective noticed..."
            mock_prompt.tags = ["mystery", "suspense"]
            mock_create_prompt.return_value = mock_prompt

            from app.routers.prompt import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/prompts")
            client = TestClient(app)

            prompt_data = {
                "title": "Mystery Plot Hook",
                "content": "The old clock struck midnight as the detective noticed...",
                "category": "plot-hooks",
                "tags": ["mystery", "suspense"]
            }

            response = client.post("", json=prompt_data)

            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["data"]["title"] == "Mystery Plot Hook"