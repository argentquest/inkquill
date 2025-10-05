# tests/test_interview_ai_writing.py

"""
Comprehensive tests for Interview and AI Writing Assistance endpoints
Tests user onboarding, personality profiling, real-time AI writing, and creative assistance
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.routers import interview as interview_router
from app.routers import ai_assisted_writing as ai_writing_router
from app.routers import ai_scene_writing as ai_scene_router
from app.routers import welcome_interview as welcome_router


class TestInterviewEndpoints:
    """Test personality assessment and user interview endpoints."""

    @pytest.mark.asyncio
    async def test_get_interview_questions_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /interview-questions - Get available interview questions."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.interview.interview_service') as mock_interview_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock questions
            mock_questions = [
                {
                    "category": "writing",
                    "question": "What genres do you enjoy writing?",
                    "options": ["Fantasy", "Sci-Fi", "Romance", "Mystery"]
                },
                {
                    "category": "experience",
                    "question": "How experienced are you as a writer?",
                    "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
                }
            ]
            mock_interview_svc.get_available_questions.return_value = mock_questions

            client = test_client_factory.create_client_with_routers(interview_router.router)

            response = client.get("/interview-questions?category=writing")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            questions = data["data"]
            assert len(questions) == 2
            assert questions[0]["category"] == "writing"

    @pytest.mark.asyncio
    async def test_submit_interview_responses_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /interview/responses - Submit interview answers."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.interview.interview_service') as mock_interview_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock analysis result
            analysis_result = {
                "personality_profile": {
                    "writing_style": "creative",
                    "preferred_genres": ["fantasy", "sci-fi"],
                    "experience_level": "intermediate",
                    "motivations": ["storytelling", "world-building"]
                },
                "recommendations": [
                    "Consider starting with fantasy world-building",
                    "Try AI-assisted character development"
                ],
                "next_steps": [
                    "Explore world-building tools",
                    "Try creating your first AI-enhanced story"
                ]
            }
            mock_interview_svc.analyze_responses.return_value = analysis_result

            client = test_client_factory.create_client_with_routers(interview_router.router)

            responses = {
                "genre_preference": "fantasy",
                "writing_experience": "intermediate",
                "creative_goals": "world-building"
            }

            response = client.post("/interview/responses", json=responses)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert "personality_profile" in result
            assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_get_user_personality_profile(self, test_client_factory, mock_authenticated_user):
        """Test GET /interview/profile - Get user's analyzed personality profile."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.interview.interview_service') as mock_interview_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock profile data
            profile_data = {
                "user_id": mock_authenticated_user.id,
                "writing_style": "narrative",
                "preferred_genres": ["fantasy", "mystery"],
                "experience_level": "advanced",
                "strengths": ["character development", "plot construction"],
                "areas_for_improvement": ["dialogue", "pacing"],
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }
            mock_interview_svc.get_user_profile.return_value = profile_data

            client = test_client_factory.create_client_with_routers(interview_router.router)

            response = client.get("/interview/profile")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            profile = data["data"]
            assert profile["writing_style"] == "narrative"
            assert "fantasy" in profile["preferred_genres"]


class TestWelcomeInterviewEndpoints:
    """Test onboarding and welcome interview functionality."""

    @pytest.mark.asyncio
    async def test_start_welcome_interview_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /welcome/start - Begin welcome/onboarding process."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.welcome_interview.welcome_service') as mock_welcome_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock welcome session
            welcome_session = {
                "session_id": "welcome_123",
                "current_step": "introduction",
                "completed_questions": [],
                "total_questions": 10,
                "estimated_time_minutes": 15
            }
            mock_welcome_svc.start_welcome_session.return_value = welcome_session

            client = test_client_factory.create_client_with_routers(welcome_router.router)

            response = client.post("/welcome/start")

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            session = data["data"]
            assert session["session_id"] == "welcome_123"
            assert session["current_step"] == "introduction"

    @pytest.mark.asyncio
    async def test_get_welcome_questions_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /welcome/questions - Get current welcome questions."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.welcome_interview.welcome_service') as mock_welcome_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock questions for current step
            questions = [
                {
                    "id": "q1",
                    "question": "What type of stories are you most interested in creating?",
                    "type": "multiple_choice",
                    "options": ["Fantasy", "Sci-Fi", "Romance", "Mystery", "Other"]
                },
                {
                    "id": "q2",
                    "question": "Have you written stories before?",
                    "type": "yes_no",
                    "options": ["Yes", "No"]
                }
            ]
            mock_welcome_svc.get_current_questions.return_value = questions

            client = test_client_factory.create_client_with_routers(welcome_router.router)

            response = client.get("/welcome/questions?session_id=welcome_123")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            question_list = data["data"]
            assert len(question_list) == 2
            assert question_list[0]["type"] == "multiple_choice"

    @pytest.mark.asyncio
    async def test_submit_welcome_answer_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /welcome/answer - Submit answer and get next question."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.welcome_interview.welcome_service') as mock_welcome_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock progress result
            progress_result = {
                "session_id": "welcome_123",
                "current_step": "writing_experience",
                "progress_percentage": 20,
                "completed_questions": 1,
                "total_questions": 10,
                "next_question": {
                    "id": "q2",
                    "question": "How would you describe your writing experience?",
                    "type": "rating"
                }
            }
            mock_welcome_svc.process_answer.return_value = progress_result

            client = test_client_factory.create_client_with_routers(welcome_router.router)

            answer_data = {
                "session_id": "welcome_123",
                "question_id": "q1",
                "answer": "Fantasy"
            }

            response = client.post("/welcome/answer", json=answer_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            progress = data["data"]
            assert progress["progress_percentage"] == 20
            assert "next_question" in progress


class TestAIAwritingAssistanceEndpoints:
    """Test real-time AI writing assistance and enhancement."""

    @pytest.mark.asyncio
    async def test_get_ai_writing_suggestions_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /ai-writing/suggestions - Get AI writing suggestions."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.ai_assisted_writing.ai_writing_service') as mock_ai_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock AI suggestions
            suggestions = {
                "context_analysis": {
                    "scene_type": "dialogue",
                    "character_emotions": ["excited", "determined"],
                    "plot_progression": "rising_action"
                },
                "improvements": [
                    {
                        "type": "dialogue_enhancement",
                        "suggestion": "Consider adding subtext to show character's true feelings",
                        "original_text": "I'm fine",
                        "improved_text": "I'm... I'm fine. Really. Everything's just perfect."
                    },
                    {
                        "type": "pacing_suggestion",
                        "suggestion": "Add sensory details to slow down the pacing",
                        "confidence": 0.85
                    }
                ],
                "character_consistency": {
                    "name": "Hero Character",
                    "traits_verified": ["brave", "compassionate"],
                    "potential_inconsistencies": []
                }
            }
            mock_ai_svc.get_writing_suggestions.return_value = suggestions

            client = test_client_factory.create_client_with_routers(ai_writing_router.router)

            content = {
                "content": "Hero pushed open the Iron Gate. The hall was empty. \"I'm fine,\" he said.",
                "context_type": "scene",
                "character_ids": [1],
                "location_id": 2
            }

            response = client.post("/ai-writing/suggestions", json=content)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            suggestions_result = data["data"]
            assert "improvements" in suggestions_result
            assert len(suggestions_result["improvements"]) == 2

    @pytest.mark.asyncio
    async def test_apply_ai_writing_enhancement_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /ai-writing/enhance - Apply AI enhancement to content."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.ai_assisted_writing.ai_writing_service') as mock_ai_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock enhanced content
            enhanced_result = {
                "original_content": "The room was dark.",
                "enhanced_content": "The room was shrouded in impenetrable darkness, lit only by the faint glow of moonlight filtering through cracked shutters. Shadows danced along the walls like restless spirits.",
                "changes_applied": [
                    "Added atmospheric description",
                    "Enhanced sensory details",
                    "Improved word choice for tension"
                ],
                "enhancement_type": "atmospheric_building",
                "confidence_score": 0.92
            }
            mock_ai_svc.apply_enhancement.return_value = enhanced_result

            client = test_client_factory.create_client_with_routers(ai_writing_router.router)

            enhancement_request = {
                "content": "The room was dark.",
                "enhancement_type": "atmospheric_building",
                "creative_intensity": "moderate"
            }

            response = client.post("/ai-writing/enhance", json=enhancement_request)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert "enhanced_content" in result
            assert result["enhancement_type"] == "atmospheric_building"

    @pytest.mark.asyncio
    async def test_generate_ai_continuations_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /ai-writing/continuations - Generate story continuations."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.ai_assisted_writing.ai_writing_service') as mock_ai_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock continuation suggestions
            continuations = {
                "original_context": "Hero entered the castle. The throne room was ahead.",
                "continuations": [
                    {
                        "continuation": "His footsteps echoed loudly in the empty corridor. The throne room doors loomed before him, engraved with ancient runes that seemed to pulse with hidden power.",
                        "style": "mysterious",
                        "tone": "tense",
                        "confidence": 0.89
                    },
                    {
                        "continuation": "Sunlight streamed through stained glass windows, casting colorful patterns on marble floors. A figure sat upon the throne, watching his approach with calculating eyes.",
                        "style": "descriptive",
                        "tone": "mysterious",
                        "confidence": 0.87
                    }
                ],
                "based_on": ["story_context", "character_personality", "world_lore"]
            }
            mock_ai_svc.generate_continuations.return_value = continuations

            client = test_client_factory.create_client_with_routers(ai_writing_router.router)

            continuation_request = {
                "current_content": "Hero entered the castle. The throne room was ahead.",
                "story_id": 1,
                "continuation_count": 2,
                "creativity_level": "balanced"
            }

            response = client.post("/ai-writing/continuations", json=continuation_request)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert len(result["continuations"]) == 2
            assert result["continuations"][0]["style"] == "mysterious"


class TestAISceneWritingEndpoints:
    """Test scene-specific AI writing assistance."""

    @pytest.mark.asyncio
    async def test_generate_scene_content_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /ai-scenes/generate - Generate complete scene content."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.ai_scene_writing.scene_ai_service') as mock_scene_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock generated scene
            generated_scene = {
                "scene_content": "The moon hung low over the misty forest as Elena crept silently through the underbrush. The ancient artifact pulsed with ethereal light in her satchel, its warmth both comforting and ominous. Footsteps echoed in the distance—her pursuers were closing in.",
                "scene_metadata": {
                    "word_count": 78,
                    "genre": "fantasy",
                    "tone": "suspenseful",
                    "key_elements": ["mystery", "pursuit", "supernatural_artifact"]
                },
                "suggestions": [
                    "Consider adding more sensory details about the artifact's warmth",
                    "The pacing builds tension effectively",
                    "Character motivation is clear"
                ],
                "character_focus": "Elena",
                "location": "Ancient Forest"
            }
            mock_scene_svc.generate_scene_content.return_value = generated_scene

            from app.routers.ai_scene_writing import router as scene_router
            client = test_client_factory.create_client_with_routers(scene_router)

            generation_request = {
                "scene_description": "Elena fleeing through forest with magical artifact",
                "character_id": 1,
                "location_id": 2,
                "genre": "fantasy",
                "target_word_count": 150,
                "tone": "suspenseful"
            }

            response = client.post("/ai-scenes/generate", json=generation_request)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert "scene_content" in result
            assert result["scene_metadata"]["tone"] == "suspenseful"

    @pytest.mark.asyncio
    async def test_improve_scene_quality_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /ai-scenes/improve - Improve existing scene content."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.ai_scene_writing.scene_ai_service') as mock_scene_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock improved scene
            improved_scene = {
                "original_content": "John walked down the street. He was tired.",
                "improved_content": "John trudged down the rain-slicked street, his shoulders hunched against the relentless downpour. Exhaustion seeped into his bones, each step a battle against the weight of the day's disappointments. Streetlights cast long, distorted shadows that danced like ghosts ahead of him.",
                "improvements_made": {
                    "pacing": "Added sensory details and internal conflict to slow pacing",
                    "description": "Enhanced atmosphere with weather and lighting",
                    "characterization": "Added emotional depth and physical mannerisms"
                },
                "quality_score": 8.5,
                "readability_score": 7.2
            }
            mock_scene_svc.improve_scene_content.return_value = improved_scene

            from app.routers.ai_scene_writing import router as scene_router
            client = test_client_factory.create_client_with_routers(scene_router)

            improvement_request = {
                "scene_content": "John walked down the street. He was tired.",
                "improvement_goals": ["add_atmosphere", "deepen_emotions", "enhance_pacing"],
                "writing_style": "literary"
            }

            response = client.post("/ai-scenes/improve", json=improvement_request)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert "improved_content" in result
            assert result["quality_score"] == 8.5
            assert "pacing" in result["improvements_made"]


class TestInterviewAIWritingIntegration:
    """Test integration between interview results and AI writing assistance."""

    @pytest.mark.asyncio
    async def test_ai_writing_style_from_interview(self, test_client_factory, mock_authenticated_user):
        """Test AI writing adapts based on user interview/personality profile."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.ai_assisted_writing.ai_writing_service') as mock_ai_svc, \
             patch('app.routers.ai_assisted_writing.interview_service') as mock_interview_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock user's interview profile
            user_profile = {
                "writing_style": "descriptive",
                "preferred_genres": ["fantasy", "mystery"],
                "experience_level": "intermediate",
                "preferred_tone": "atmospheric"
            }
            mock_interview_svc.get_user_profile.return_value = user_profile

            # Mock personalized AI suggestions
            personalized_suggestions = {
                "adapted_for_user": True,
                "user_style_preference": "descriptive",
                "genre_adaptations": ["fantasy", "mystery"],
                "tone_adjustment": "atmospheric",
                "improvements": [
                    {
                        "type": "style_alignment",
                        "suggestion": "Added descriptive atmospheric elements you prefer",
                        "example": "Rather than 'It was foggy', suggested 'Mist clung to the ancient stones like whispered secrets'"
                    }
                ]
            }
            mock_ai_svc.get_personalized_suggestions.return_value = personalized_suggestions

            client = test_client_factory.create_client_with_routers(ai_writing_router.router)

            content = {
                "content": "The old house stood at the end of the street.",
                "adapt_to_user_profile": True
            }

            response = client.post("/ai-writing/suggestions", json=content)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            suggestions = data["data"]
            assert suggestions["adapted_for_user"] is True
            assert suggestions["user_style_preference"] == "descriptive"

    @pytest.mark.asyncio
    async def test_scene_generation_with_interview_context(self, test_client_factory, mock_authenticated_user):
        """Test scene generation incorporates interview-derived preferences."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.ai_scene_writing.scene_ai_service') as mock_scene_svc, \
             patch('app.routers.ai_scene_writing.interview_service') as mock_interview_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock comprehensive context
            interview_context = {
                "writing_experience": "advanced",
                "genre_preferences": ["urban_fantasy", "historical"],
                "character_types": ["flawed_protag", "mysterious_mentor"],
                "plot_preferences": ["character_driven", "mysteries"],
                "atmosphere_preference": "moody"
            }
            mock_interview_svc.get_user_writing_context.return_value = interview_context

            # Mock scene tailored to user preferences
            context_aware_scene = {
                "scene_content": "Detective Reyes adjusted her trench coat against the autumn chill, the city lights reflecting off rain-slicked cobblestones. The old bookstore loomed ahead, its windows fogged and mysterious. Something about this case felt personal - too personal.",
                "incorporated_preferences": {
                    "atmosphere": "moody_with_weather",
                    "character_archetype": "flawed_detective",
                    "plot_element": "personal_mystery",
                    "writing_complexity": "advanced_level"
                },
                "personalization_score": 0.93
            }
            mock_scene_svc.generate_context_aware_scene.return_value = context_aware_scene

            from app.routers.ai_scene_writing import router as scene_router
            client = test_client_factory.create_client_with_routers(scene_router)

            generation_request = {
                "scene_concept": "detective investigating mysterious bookstore",
                "use_user_context": True,
                "creativity_boost": "balanced"
            }

            response = client.post("/ai-scenes/generate", json=generation_request)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert result["incorporated_preferences"]["atmosphere"] == "moody_with_weather"
            assert result["personalization_score"] == 0.93


class TestInterviewAIValidation:
    """Test input validation and error handling for interview/AI endpoints."""

    @pytest.mark.asyncio
    async def test_invalid_interview_responses_error(self, test_client_factory, mock_authenticated_user):
        """Test POST /interview/responses - Invalid responses validation."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(interview_router.router)

            # Invalid responses (missing required fields, wrong formats)
            invalid_responses = {
                "invalid_field": "not_allowed",
                "genre_preference": ["should_be_string"],
                "experience_level": "nonexistent_level"
            }

            response = client.post("/interview/responses", json=invalid_responses)

            # Should return validation error
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ai_writing_content_too_short_error(self, test_client_factory, mock_authenticated_user):
        """Test POST /ai-writing/suggestions - Content too short for meaningful suggestions."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(ai_writing_router.router)

            # Content too short for analysis
            short_content = {
                "content": "Hi",
                "context_type": "scene"
            }

            response = client.post("/ai-writing/suggestions", json=short_content)

            # Should return 422 for minimum content requirements
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_scene_generation_unauthenticated_error(self, test_client_factory):
        """Test POST /ai-scenes/generate - Requires authentication."""
        from app.routers.ai_scene_writing import router as scene_router
        client = test_client_factory.create_client_with_routers(scene_router)

        generation_request = {
            "scene_description": "Test scene",
            "character_id": 1
        }

        # No auth header - should fail
        response = client.post("/ai-scenes/generate", json=generation_request)

        # Should return 401 Unauthorized
        assert response.status_code == 401