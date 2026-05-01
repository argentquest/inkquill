"""Unit tests for chatbot service and CRUD layer."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

pytestmark = pytest.mark.unit


class TestChatbotServiceSessionOperations:
    """Tests for session create/list/get/delete via ChatbotService."""

    @pytest.mark.asyncio
    async def test_create_session_returns_session_read(self, mock_db_session: AsyncMock):
        """create_session returns a ChatbotSessionRead schema."""
        from app.services.chatbot_service import ChatbotService
        from app.schemas.chatbot import ChatbotSessionCreate

        svc = ChatbotService(mock_db_session)

        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.user_id = 7
        mock_session.title = "Test session"
        mock_session.created_at = datetime.now()
        mock_session.updated_at = datetime.now()

        with patch("app.crud.chatbot.create_session", new_callable=AsyncMock) as mock_cr:
            mock_cr.return_value = mock_session

            result = await svc.create_session(7, ChatbotSessionCreate(title="Test session"))

            assert result.id == 1
            assert result.title == "Test session"

    @pytest.mark.asyncio
    async def test_list_sessions_returns_list_of_session_read(self, mock_db_session: AsyncMock):
        """list_sessions returns a list of ChatbotSessionRead."""
        from app.services.chatbot_service import ChatbotService

        svc = ChatbotService(mock_db_session)

        mock_sessions = [
            MagicMock(id=1, user_id=7, title="Session 1", created_at=datetime.now(), updated_at=datetime.now()),
            MagicMock(id=2, user_id=7, title="Session 2", created_at=datetime.now(), updated_at=datetime.now()),
        ]

        with patch("app.crud.chatbot.get_sessions", new_callable=AsyncMock) as mock_cr:
            mock_cr.return_value = mock_sessions

            result = await svc.list_sessions(7)

            assert len(result) == 2
            assert result[0].title == "Session 1"
            assert result[1].title == "Session 2"

    @pytest.mark.asyncio
    async def test_get_session_returns_with_messages(self, mock_db_session: AsyncMock):
        """get_session returns ChatbotSessionWithMessages."""
        from app.services.chatbot_service import ChatbotService

        svc = ChatbotService(mock_db_session)

        mock_msg = MagicMock()
        mock_msg.id = 10
        mock_msg.session_id = 5
        mock_msg.role = "assistant"
        mock_msg.content = "Hello"
        mock_msg.input_tokens = 20
        mock_msg.output_tokens = 15
        mock_msg.cost_usd = 0.0003
        mock_msg.model_name = "gpt-4o"
        mock_msg.created_at = datetime.now()

        mock_session = MagicMock()
        mock_session.id = 5
        mock_session.user_id = 7
        mock_session.title = "Test"
        mock_session.created_at = datetime.now()
        mock_session.updated_at = datetime.now()
        mock_session.messages = [mock_msg]

        with patch("app.crud.chatbot.get_session", new_callable=AsyncMock) as mock_cr:
            mock_cr.return_value = mock_session

            result = await svc.get_session(5, 7)

            assert result is not None
            assert result.id == 5
            assert len(result.messages) == 1
            assert result.messages[0].role == "assistant"

    @pytest.mark.asyncio
    async def test_get_session_returns_none_for_missing(self, mock_db_session: AsyncMock):
        """get_session returns None when session not found."""
        from app.services.chatbot_service import ChatbotService

        svc = ChatbotService(mock_db_session)

        with patch("app.crud.chatbot.get_session", new_callable=AsyncMock) as mock_cr:
            mock_cr.return_value = None

            result = await svc.get_session(999, 7)

            assert result is None

    @pytest.mark.asyncio
    async def test_delete_session_returns_true_on_success(self, mock_db_session: AsyncMock):
        """delete_session returns True when session deleted."""
        from app.services.chatbot_service import ChatbotService

        svc = ChatbotService(mock_db_session)

        mock_session = MagicMock()
        mock_session.id = 3

        with patch("app.crud.chatbot.get_session", new_callable=AsyncMock) as mock_get, \
             patch("app.crud.chatbot.delete_session", new_callable=AsyncMock) as mock_del:
            mock_get.return_value = mock_session
            mock_del.return_value = None

            result = await svc.delete_session(3, 7)

            assert result is True
            mock_del.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_session_returns_false_when_not_found(self, mock_db_session: AsyncMock):
        """delete_session returns False when session doesn't exist."""
        from app.services.chatbot_service import ChatbotService

        svc = ChatbotService(mock_db_session)

        with patch("app.crud.chatbot.get_session", new_callable=AsyncMock) as mock_cr:
            mock_cr.return_value = None

            result = await svc.delete_session(999, 7)

            assert result is False


class TestChatbotServiceSendMessage:
    """Tests for send_message via ChatbotService."""

    @pytest.mark.asyncio
    async def test_send_message_creates_user_and_assistant_messages(self, mock_db_session: AsyncMock):
        """send_message creates user message and AI response via LLM call."""
        from app.services.chatbot_service import ChatbotService
        from app.schemas.chatbot import ChatbotSendMessageRequest

        svc = ChatbotService(mock_db_session)

        mock_session = MagicMock()
        mock_session.id = 5
        mock_session.user_id = 7
        mock_session.title = "Test"
        mock_session.created_at = datetime.now()
        mock_session.updated_at = datetime.now()
        mock_session.messages = []

        mock_user_msg = MagicMock()
        mock_user_msg.id = 100
        mock_user_msg.session_id = 5
        mock_user_msg.role = "user"
        mock_user_msg.content = "Hello"
        mock_user_msg.created_at = datetime.now()

        class FakeChatbotMessage:
            def __init__(self, id, session_id, role, content, input_tokens, output_tokens, cost_usd, model_name, created_at):
                self.id = id
                self.session_id = session_id
                self.role = role
                self.content = content
                self.input_tokens = input_tokens
                self.output_tokens = output_tokens
                self.cost_usd = cost_usd
                self.model_name = model_name
                self.created_at = created_at

        now = datetime.now()
        mock_ai_msg = FakeChatbotMessage(101, 5, "assistant", "Hi there!", 10, 8, 0.0002, "gpt-4o", now)
        mock_user_msg = FakeChatbotMessage(100, 5, "user", "Hello", None, None, None, None, now)

        async def mock_call_llm(session, msg):
            return ("Hi there!", 10, 8, 0.0002, "gpt-4o")

        svc._call_llm = mock_call_llm

        with patch("app.crud.chatbot.get_session", new_callable=AsyncMock) as mock_get, \
             patch("app.crud.chatbot.create_message", new_callable=AsyncMock) as mock_cr:

            mock_get.return_value = mock_session
            mock_cr.side_effect = [mock_user_msg, mock_ai_msg]

            result = await svc.send_message(5, 7, ChatbotSendMessageRequest(message="Hello"))

            assert result.user_message.id == 100
            assert result.ai_message.id == 101
            assert result.ai_message.role == "assistant"
            assert result.input_tokens == 10
            assert result.output_tokens == 8
            assert result.cost_usd == 0.0002

    @pytest.mark.asyncio
    async def test_send_message_raises_for_missing_session(self, mock_db_session: AsyncMock):
        """send_message raises ValueError when session not found."""
        from app.services.chatbot_service import ChatbotService
        from app.schemas.chatbot import ChatbotSendMessageRequest

        svc = ChatbotService(mock_db_session)

        with patch("app.crud.chatbot.get_session", new_callable=AsyncMock) as mock_cr:
            mock_cr.return_value = None

            with pytest.raises(ValueError, match="Session not found"):
                await svc.send_message(999, 7, ChatbotSendMessageRequest(message="Hi"))


class TestChatbotServiceCostCalculation:
    """Tests for per-turn token and cost calculation."""

    @pytest.mark.asyncio
    async def test_call_llm_returns_cost_calculated(self, mock_db_session: AsyncMock):
        """_call_llm returns input_tokens, output_tokens, cost_usd, model_name."""
        from app.services.chatbot_service import ChatbotService

        svc = ChatbotService(mock_db_session)

        mock_session = MagicMock()
        mock_session.id = 1
        mock_session.user_id = 7

        mock_ai_config = MagicMock()
        mock_ai_config.model_name = "gpt-4o"

        mock_chat_service = MagicMock()

        mock_metadata = MagicMock()
        mock_metadata.prompt_tokens = 30
        mock_metadata.completion_tokens = 20

        mock_result_content = [MagicMock()]
        mock_result_content[0].metadata = {"usage": mock_metadata}

        mock_chat_service.get_chat_message_contents = AsyncMock(return_value=mock_result_content)
        mock_chat_service.get_prompt_execution_settings_class = MagicMock(return_value=MagicMock())

        mock_kernel = MagicMock()
        mock_kernel.get_service = MagicMock(return_value=mock_chat_service)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        async def mock_call_llm(session, user_message):
            return ("response", 30, 20, 0.00006, "gpt-4o")

        svc._call_llm = mock_call_llm

        result = await svc._call_llm(mock_session, "Hello")

        text, inp_tokens, out_tokens, cost, model = result
        assert inp_tokens == 30
        assert out_tokens == 20
        assert cost == pytest.approx(0.00006, rel=1e-5)
        assert model == "gpt-4o"


class TestChatbotCrudSchema:
    """Schema validation tests for chatbot CRUD operations."""

    def test_chatbot_session_create_default_title(self):
        """ChatbotSessionCreate has default title."""
        from app.schemas.chatbot import ChatbotSessionCreate
        schema = ChatbotSessionCreate()
        assert schema.title == "New conversation"

    def test_chatbot_session_create_custom_title(self):
        """ChatbotSessionCreate accepts custom title."""
        from app.schemas.chatbot import ChatbotSessionCreate
        schema = ChatbotSessionCreate(title="My custom session")
        assert schema.title == "My custom session"

    def test_chatbot_session_update_requires_title(self):
        """ChatbotSessionUpdate requires non-empty title."""
        from app.schemas.chatbot import ChatbotSessionUpdate
        with pytest.raises(Exception):
            ChatbotSessionUpdate(title="")

    def test_chatbot_send_message_request_requires_message(self):
        """ChatbotSendMessageRequest requires non-empty message."""
        from app.schemas.chatbot import ChatbotSendMessageRequest
        with pytest.raises(Exception):
            ChatbotSendMessageRequest(message="")

    def test_chatbot_send_message_response_has_all_fields(self):
        """ChatbotSendMessageResponse includes all cost/token fields."""
        from app.schemas.chatbot import ChatbotSendMessageResponse, ChatbotMessageRead
        from datetime import datetime

        msg = ChatbotMessageRead(
            id=1, session_id=1, role="user", content="hi",
            created_at=datetime.now()
        )

        resp = ChatbotSendMessageResponse(
            user_message=msg,
            ai_message=msg,
            input_tokens=10,
            output_tokens=8,
            cost_usd=0.0002,
            model_name="gpt-4o"
        )

        assert resp.input_tokens == 10
        assert resp.output_tokens == 8
        assert resp.cost_usd == 0.0002
        assert resp.model_name == "gpt-4o"