# tests/test_brainstorm_story_chat.py

"""
Comprehensive tests for Brainstorm and Story Chat endpoints
Tests creative ideation, collaborative writing, and real-time story development
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.routers import brainstorm as brainstorm_router
from app.routers import story_chat as story_chat_router
from app.routers import world_chat as world_chat_router


class TestBrainstormEndpoints:
    """Test creative brainstorming and ideation tools."""

    @pytest.mark.asyncio
    async def test_start_brainstorm_session_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /brainstorm/start - Start new brainstorming session."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.brainstorm.brainstorm_service') as mock_brainstorm_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock brainstorm session
            session_data = {
                "session_id": "brainstorm_123",
                "session_type": "character_development",
                "topic": "Antagonist Motivations",
                "participants": [mock_authenticated_user.id],
                "max_participants": 5,
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            mock_brainstorm_svc.start_session.return_value = session_data

            client = test_client_factory.create_client_with_routers(brainstorm_router.router)

            session_request = {
                "topic": "Antagonist Motivations",
                "session_type": "character_development",
                "world_id": 1,
                "story_id": 2,
                "max_participants": 5
            }

            response = client.post("/brainstorm/start", json=session_request)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            session = data["data"]
            assert session["session_type"] == "character_development"
            assert session["topic"] == "Antagonist Motivations"
            assert session["status"] == "active"

    @pytest.mark.asyncio
    async def test_generate_brainstorm_ideas_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /brainstorm/{session_id}/ideas - Generate AI-powered brainstorming ideas."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.brainstorm.brainstorm_service') as mock_brainstorm_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock generated ideas
            generated_ideas = {
                "session_id": "brainstorm_123",
                "idea_category": "plot_twists",
                "ideas": [
                    {
                        "id": "idea_1",
                        "content": "The protagonist discovers they are actually an AI construct designed to test human nature",
                        "category": "identity_reveal",
                        "novelty_score": 0.95,
                        "feasibility_score": 0.85,
                        "tags": ["science_fiction", "philosophical", "twist"],
                        "votes": 0,
                        "author_id": mock_authenticated_user.id
                    },
                    {
                        "id": "idea_2",
                        "content": "The antagonist is revealed to be a time-displaced version of the protagonist",
                        "category": "character_connection",
                        "novelty_score": 0.88,
                        "feasibility_score": 0.92,
                        "tags": ["time_travel", "character_driven", "twist"],
                        "votes": 0,
                        "author_id": mock_authenticated_user.id
                    }
                ],
                "total_ideas": 2,
                "generation_prompt": "Generate plot twist ideas that subvert reader expectations"
            }
            mock_brainstorm_svc.generate_ideas.return_value = generated_ideas

            client = test_client_factory.create_client_with_routers(brainstorm_router.router)

            generation_request = {
                "idea_category": "plot_twists",
                "number_of_ideas": 2,
                "creativity_level": "high",
                "context": {
                    "genre": "sci-fi",
                    "main_theme": "identity",
                    "target_audience": "adult"
                }
            }

            response = client.post("/brainstorm/brainstorm_123/ideas", json=generation_request)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert len(result["ideas"]) == 2
            assert result["ideas"][0]["novelty_score"] == 0.95
            assert result["ideas"][1]["category"] == "character_connection"

    @pytest.mark.asyncio
    async def test_vote_brainstorm_idea_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /brainstorm/ideas/{idea_id}/vote - Vote on brainstorm idea."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.brainstorm.brainstorm_service') as mock_brainstorm_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock vote result
            vote_result = {
                "idea_id": "idea_1",
                "session_id": "brainstorm_123",
                "user_vote": "upvote",
                "total_upvotes": 5,
                "total_downvotes": 1,
                "score": 4,
                "user_id": mock_authenticated_user.id
            }
            mock_brainstorm_svc.cast_vote.return_value = vote_result

            client = test_client_factory.create_client_with_routers(brainstorm_router.router)

            vote_data = {"vote_type": "upvote"}

            response = client.post("/brainstorm/ideas/idea_1/vote", json=vote_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            vote_info = data["data"]
            assert vote_info["user_vote"] == "upvote"
            assert vote_info["score"] == 4

    @pytest.mark.asyncio
    async def test_get_brainstorm_sessions_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /brainstorm/sessions - Get user's brainstorm sessions."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.brainstorm.brainstorm_service') as mock_brainstorm_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock sessions list
            sessions = [
                {
                    "session_id": "brainstorm_123",
                    "topic": "Character Arcs",
                    "session_type": "character_development",
                    "status": "active",
                    "participants": 3,
                    "idea_count": 12,
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_activity": "2024-01-15T14:20:00Z"
                },
                {
                    "session_id": "brainstorm_456",
                    "topic": "World Politics",
                    "session_type": "world_building",
                    "status": "completed",
                    "participants": 1,
                    "idea_count": 8,
                    "created_at": "2024-01-10T09:00:00Z",
                    "last_activity": "2024-01-10T12:15:00Z"
                }
            ]
            mock_brainstorm_svc.get_user_sessions.return_value = sessions

            client = test_client_factory.create_client_with_routers(brainstorm_router.router)

            response = client.get("/brainstorm/sessions?status=active")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            session_list = data["data"]
            assert len(session_list) == 2
            assert session_list[0]["status"] == "active"
            assert session_list[1]["topic"] == "World Politics"

    @pytest.mark.asyncio
    async def test_end_brainstorm_session_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /brainstorm/{session_id}/end - End brainstorm session."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.brainstorm.brainstorm_service') as mock_brainstorm_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock session end result
            end_result = {
                "session_id": "brainstorm_123",
                "status": "completed",
                "ended_at": datetime.utcnow().isoformat(),
                "final_statistics": {
                    "total_ideas": 15,
                    "total_participants": 3,
                    "ideas_pre_selected": 5,
                    "most_voted_idea": "idea_7"
                },
                "summary_report": {
                    "top_categories": ["plot_twists", "character_development"],
                    "collaboration_score": 0.85,
                    "ideas_per_participant": 5.0
                }
            }
            mock_brainstorm_svc.end_session.return_value = end_result

            client = test_client_factory.create_client_with_routers(brainstorm_router.router)

            response = client.post("/brainstorm/brainstorm_123/end")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert result["status"] == "completed"
            assert "final_statistics" in result
            assert result["final_statistics"]["total_ideas"] == 15


class TestStoryChatEndpoints:
    """Test story chat and collaborative writing functionality."""

    @pytest.mark.asyncio
    async def test_send_story_chat_message_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /story-chat/{story_id}/messages - Send story chat message."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story_chat.story_chat_service') as mock_chat_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock sent message
            sent_message = {
                "message_id": "msg_123",
                "story_id": 1,
                "user_id": mock_authenticated_user.id,
                "username": mock_authenticated_user.username,
                "content": "What if we add a twist where the hero discovers they're adopted?",
                "message_type": "text",
                "timestamp": datetime.utcnow().isoformat(),
                "edit_count": 0,
                "attachments": []
            }
            mock_chat_svc.send_message.return_value = sent_message

            client = test_client_factory.create_client_with_routers(story_chat_router.router)

            message_data = {
                "content": "What if we add a twist where the hero discovers they're adopted?",
                "message_type": "text"
            }

            response = client.post("/story-chat/1/messages", json=message_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            message = data["data"]
            assert message["content"] == "What if we add a twist where the hero discovers they're adopted?"
            assert message["user_id"] == mock_authenticated_user.id

    @pytest.mark.asyncio
    async def test_get_story_chat_messages_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /story-chat/{story_id}/messages - Get story chat messages."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story_chat.story_chat_service') as mock_chat_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock chat messages
            messages = [
                {
                    "message_id": "msg_001",
                    "user_id": 1,
                    "username": "collaborator1",
                    "content": "Great scene! The tension is building nicely.",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "message_type": "comment",
                    "reply_to": None
                },
                {
                    "message_id": "msg_002",
                    "user_id": 2,
                    "username": "collaborator2",
                    "content": "Agreed! Maybe add more sensory details?",
                    "timestamp": "2024-01-15T10:35:00Z",
                    "message_type": "suggestion",
                    "reply_to": "msg_001",
                    "attachments": [
                        {"type": "text_selection", "scene_id": 3, "text": "The room was quiet"}
                    ]
                },
                {
                    "message_id": "msg_003",
                    "user_id": mock_authenticated_user.id,
                    "username": mock_authenticated_user.username,
                    "content": "Thanks! Let me revise that section.",
                    "timestamp": "2024-01-15T10:40:00Z",
                    "message_type": "acknowledgment",
                    "reply_to": "msg_002"
                }
            ]
            mock_chat_svc.get_messages.return_value = messages

            client = test_client_factory.create_client_with_routers(story_chat_router.router)

            response = client.get("/story-chat/1/messages?limit=50")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            message_list = data["data"]
            assert len(message_list) == 3
            assert message_list[2]["user_id"] == mock_authenticated_user.id
            assert message_list[1]["reply_to"] == "msg_001"

    @pytest.mark.asyncio
    async def test_create_story_chat_session_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /story-chat/{story_id}/sessions - Create new chat session."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story_chat.story_chat_service') as mock_chat_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock chat session
            chat_session = {
                "session_id": "chat_session_123",
                "story_id": 1,
                "title": "Chapter 3 Discussion",
                "created_by": mock_authenticated_user.id,
                "participants": [mock_authenticated_user.id],
                "is_active": True,
                "topic_tags": ["plot", "characters", "scene"],
                "ai_participation_enabled": True,
                "created_at": datetime.utcnow().isoformat()
            }
            mock_chat_svc.create_session.return_value = chat_session

            client = test_client_factory.create_client_with_routers(story_chat_router.router)

            session_data = {
                "title": "Chapter 3 Discussion",
                "topic_tags": ["plot", "characters", "scene"],
                "include_ai_participant": True,
                "max_participants": 8
            }

            response = client.post("/story-chat/1/sessions", json=session_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            session = data["data"]
            assert session["title"] == "Chapter 3 Discussion"
            assert session["ai_participation_enabled"] is True
            assert "plot" in session["topic_tags"]

    @pytest.mark.asyncio
    async def test_add_story_chat_participant_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /story-chat/sessions/{session_id}/participants - Add participant."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story_chat.story_chat_service') as mock_chat_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock participant addition
            participant_result = {
                "session_id": "chat_session_123",
                "user_id": 3,
                "username": "new_collaborator",
                "role": "contributor",
                "added_by": mock_authenticated_user.id,
                "joined_at": datetime.utcnow().isoformat(),
                "total_participants": 4
            }
            mock_chat_svc.add_participant.return_value = participant_result

            client = test_client_factory.create_client_with_routers(story_chat_router.router)

            participant_data = {"user_id": 3, "role": "contributor"}

            response = client.post("/story-chat/sessions/chat_session_123/participants", json=participant_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert result["user_id"] == 3
            assert result["role"] == "contributor"
            assert result["total_participants"] == 4


class TestWorldChatEndpoints:
    """Test world-building collaborative chat functionality."""

    @pytest.mark.asyncio
    async def test_send_world_chat_message_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /world-chat/{world_id}/messages - Send world chat message."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world_chat.world_chat_service') as mock_chat_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock sent message
            sent_message = {
                "message_id": "world_msg_123",
                "world_id": 1,
                "user_id": mock_authenticated_user.id,
                "username": mock_authenticated_user.username,
                "content": "The capital city should have a river running through it, with ancient bridges.",
                "message_type": "location_idea",
                "timestamp": datetime.utcnow().isoformat(),
                "element_references": [
                    {"type": "location", "id": 2, "name": "Capital City"}
                ],
                "suggested_actions": [
                    {"action": "create_location", "data": {"name": "Grand River"}}
                ]
            }
            mock_chat_svc.send_message.return_value = sent_message

            client = test_client_factory.create_client_with_routers(world_chat_router.router)

            message_data = {
                "content": "The capital city should have a river running through it, with ancient bridges.",
                "message_type": "location_idea",
                "element_references": [{"type": "location", "id": 2}]
            }

            response = client.post("/world-chat/1/messages", json=message_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            message = data["data"]
            assert message["message_type"] == "location_idea"
            assert len(message["suggested_actions"]) == 1
            assert message["suggested_actions"][0]["action"] == "create_location"

    @pytest.mark.asyncio
    async def test_get_world_chat_suggestions_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /world-chat/{world_id}/suggestions - Get context-aware suggestions."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world_chat.world_chat_service') as mock_chat_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock context-aware suggestions
            suggestions = {
                "world_id": 1,
                "current_context": {
                    "recent_discussions": ["magic_system", "political_structure"],
                    "incomplete_elements": ["royal_family_lineage", "border_conflicts"],
                    "popular_themes": ["intrigue", "forbidden_magic"]
                },
                "suggestions": [
                    {
                        "type": "development_question",
                        "suggestion": "How does the royal succession work?",
                        "relevance_score": 0.92,
                        "based_on": ["political_structure", "royal_family_gap"]
                    },
                    {
                        "type": "world_building_idea",
                        "suggestion": "Consider adding magical academies where young nobles learn state-sanctioned spells",
                        "relevance_score": 0.88,
                        "element_types": ["locations", "organizations", "lore"]
                    },
                    {
                        "type": "consistency_check",
                        "suggestion": "Review how border conflicts affect the trade routes",
                        "relevance_score": 0.85,
                        "referenced_elements": ["Northern Mountains", "Eastern Trade Road"]
                    }
                ],
                "collaboration_stats": {
                    "active_participants": 3,
                    "ideas_this_week": 12,
                    "most_contributed_element": "magic_system"
                }
            }
            mock_chat_svc.get_suggestions.return_value = suggestions

            client = test_client_factory.create_client_with_routers(world_chat_router.router)

            response = client.get("/world-chat/1/suggestions")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert len(result["suggestions"]) == 3
            assert result["suggestions"][0]["type"] == "development_question"
            assert result["current_context"]["popular_themes"] == ["intrigue", "forbidden_magic"]

    @pytest.mark.asyncio
    async def test_create_world_chat_focus_topic_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /world-chat/{world_id}/focus - Create focused discussion topic."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world_chat.world_chat_service') as mock_chat_svc, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock focus topic creation
            focus_topic = {
                "focus_id": "focus_123",
                "world_id": 1,
                "topic": "Magic System Consistency",
                "description": "Ensuring magic rules and limitations are consistent across all elements",
                "created_by": mock_authenticated_user.id,
                "participants_required": 2,
                "current_participants": 1,
                "element_types": ["lore_items", "character_abilities"],
                "specific_elements": ["Fire Magic Lore", "Aether Crystal Lore"],
                "discussion_goals": [
                    "Define magic energy source",
                    "Set clear limitations and costs",
                    "Ensure character powers fit system"
                ],
                "status": "gathering_participants",
                "created_at": datetime.utcnow().isoformat()
            }
            mock_chat_svc.create_focus_topic.return_value = focus_topic

            client = test_client_factory.create_client_with_routers(world_chat_router.router)

            focus_data = {
                "topic": "Magic System Consistency",
                "description": "Ensuring magic rules and limitations are consistent across all elements",
                "element_types": ["lore_items", "character_abilities"],
                "discussion_goals": [
                    "Define magic energy source",
                    "Set clear limitations and costs"
                ],
                "participants_required": 2
            }

            response = client.post("/world-chat/1/focus", json=focus_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            topic = data["data"]
            assert topic["topic"] == "Magic System Consistency"
            assert len(topic["discussion_goals"]) == 2
            assert topic["element_types"] == ["lore_items", "character_abilities"]

    @pytest.mark.asyncio
    async def test_join_world_chat_focus_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /world-chat/focus/{focus_id}/join - Join focused discussion."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world_chat.world_chat_service') as mock_chat_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock join result
            join_result = {
                "focus_id": "focus_123",
                "user_id": mock_authenticated_user.id,
                "role": "contributor",
                "joined_at": datetime.utcnow().isoformat(),
                "current_participants": 3,
                "participants_required": 3,
                "status": "discussion_active"
            }
            mock_chat_svc.join_focus_topic.return_value = join_result

            client = test_client_factory.create_client_with_routers(world_chat_router.router)

            response = client.post("/world-chat/focus/focus_123/join")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert result["role"] == "contributor"
            assert result["status"] == "discussion_active"
            assert result["current_participants"] == 3


class TestBrainstormStoryChatIntegration:
    """Test integration between brainstorming, story chat, and world building."""

    @pytest.mark.asyncio
    async def test_brainstorm_idea_to_story_chat_success(self, test_client_factory, mock_authenticated_user):
        """Test converting brainstorm idea to story chat discussion."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.brainstorm.brainstorm_service') as mock_brainstorm_svc, \
             patch('app.routers.story_chat.story_chat_service') as mock_chat_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock idea conversion
            conversion_result = {
                "original_idea": "idea_123",
                "brainstorm_session": "brainstorm_456",
                "chat_session": "chat_session_789",
                "converted_content": "The protagonist discovers they're actually an AI construct designed to test human nature",
                "transition_explanation": "This idea could make for an interesting philosophical discussion in the story's themes",
                "suggested_participants": [mock_authenticated_user.id, 4, 7],  # Include original brainstorm participants
                "created_messages": [
                    {
                        "message_id": "msg_001",
                        "content": "Let's explore this AI identity idea further...",
                        "author_id": mock_authenticated_user.id
                    }
                ]
            }
            mock_brainstorm_svc.convert_idea_to_discussion.return_value = conversion_result

            client = test_client_factory.create_client_with_routers(brainstorm_router.router)

            conversion_data = {
                "idea_id": "idea_123",
                "target_type": "story_chat",
                "story_id": 1,
                "include_original_participants": True
            }

            response = client.post("/brainstorm/convert-idea", json=conversion_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert result["chat_session"] == "chat_session_789"
            assert len(result["suggested_participants"]) == 3
            assert "converted_content" in result

    @pytest.mark.asyncio
    async def test_world_chat_element_creation_from_discussion(self, test_client_factory, mock_authenticated_user):
        """Test creating world elements directly from chat discussions."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world_chat.world_chat_service') as mock_chat_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock element creation from chat
            element_creation = {
                "action_executed": "create_location",
                "element_data": {
                    "id": 15,
                    "name": "Crystal Caverns",
                    "type": "location",
                    "description": "Massive underground caverns filled with glowing crystals used in magical rituals",
                    "world_id": 1
                },
                "trigger_message": "world_msg_123",
                "created_from_discussion": "Extensive underground crystal formations perfect for magical ceremonies",
                "suggested_connections": [
                    {"type": "character", "id": 5, "reason": "Crystal magic practitioner"},
                    {"type": "lore_item", "id": 8, "reason": "Ancient crystal artifacts found here"}
                ],
                "participants_involved": [mock_authenticated_user.id, 3, 5]
            }
            mock_chat_svc.execute_suggested_action.return_value = element_creation

            client = test_client_factory.create_client_with_routers(world_chat_router.router)

            action_data = {
                "action_id": "create_location",
                "message_id": "world_msg_123",
                "data": {
                    "name": "Crystal Caverns",
                    "description": "Massive underground caverns filled with glowing crystals used in magical rituals"
                }
            }

            response = client.post("/world-chat/1/execute-action", json=action_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            result = data["data"]
            assert result["action_executed"] == "create_location"
            assert result["element_data"]["name"] == "Crystal Caverns"
            assert len(result["suggested_connections"]) == 2


class TestBrainstormStoryChatValidation:
    """Test input validation and error handling."""

    @pytest.mark.asyncio
    async def test_brainstorm_session_invalid_topic_error(self, test_client_factory, mock_authenticated_user):
        """Test POST /brainstorm/start - Invalid topic validation."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(brainstorm_router.router)

            # Invalid topic (too short, empty)
            invalid_session = {
                "topic": "",  # Empty topic
                "session_type": "invalid_type",
                "max_participants": 1000  # Invalid number
            }

            response = client.post("/brainstorm/start", json=invalid_session)

            # Should return validation error
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_story_chat_message_too_long_error(self, test_client_factory, mock_authenticated_user):
        """Test POST /story-chat/{story_id}/messages - Message too long validation."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(story_chat_router.router)

            # Message exceeding reasonable length
            very_long_message = {
                "content": "x" * 10001,  # 10,001 characters
                "message_type": "text"
            }

            response = client.post("/story-chat/1/messages", json=very_long_message)

            # Should return validation error for message length
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_world_chat_unauthorized_world_access_error(self, test_client_factory, mock_authenticated_user):
        """Test POST /world-chat/{world_id}/messages - No access to private world."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world_chat.world_chat_service') as mock_chat_svc:

            mock_get_user.return_value = mock_authenticated_user
            mock_chat_svc.get_world_access.return_value = False  # No access

            client = test_client_factory.create_client_with_routers(world_chat_router.router)

            message_data = {
                "content": "Trying to post to private world",
                "message_type": "text"
            }

            response = client.post("/world-chat/99/messages", json=message_data)

            # Should return 403 Forbidden (or 404 for world not found)
            assert response.status_code in [403, 404]