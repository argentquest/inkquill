"""Service layer for standalone chatbot sessions."""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.crud import chatbot as chatbot_crud
from app.models.chatbot_session import ChatbotSession
from app.schemas.chatbot import (
    ChatbotSessionCreate,
    ChatbotSessionRead,
    ChatbotSessionWithMessages,
    ChatbotMessageRead,
    ChatbotSendMessageRequest,
    ChatbotSendMessageResponse,
)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a concise, helpful writing assistant. "
    "Keep responses focused and clear. "
    "If the user is working on a story or care update, help them move forward practically."
)


class ChatbotService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, user_id: int, payload: ChatbotSessionCreate) -> ChatbotSessionRead:
        session = await chatbot_crud.create_session(self.db, user_id, payload.title)
        return ChatbotSessionRead.model_validate(session)

    async def list_sessions(self, user_id: int) -> List[ChatbotSessionRead]:
        sessions = await chatbot_crud.get_sessions(self.db, user_id)
        return [ChatbotSessionRead.model_validate(s) for s in sessions]

    async def get_session(self, session_id: int, user_id: int) -> Optional[ChatbotSessionWithMessages]:
        session = await chatbot_crud.get_session(self.db, session_id, user_id)
        if not session:
            return None
        return ChatbotSessionWithMessages.model_validate(session)

    async def delete_session(self, session_id: int, user_id: int) -> bool:
        session = await chatbot_crud.get_session(self.db, session_id, user_id)
        if not session:
            return False
        await chatbot_crud.delete_session(self.db, session)
        return True

    async def send_message(
        self,
        session_id: int,
        user_id: int,
        request: ChatbotSendMessageRequest,
    ) -> ChatbotSendMessageResponse:
        session = await chatbot_crud.get_session(self.db, session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        user_msg = await chatbot_crud.create_message(
            self.db, session_id=session_id, role="user", content=request.message
        )

        ai_text, input_tokens, output_tokens, cost_usd, model_name = await self._call_llm(
            session, request.message
        )

        ai_msg = await chatbot_crud.create_message(
            self.db,
            session_id=session_id,
            role="assistant",
            content=ai_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            model_name=model_name,
        )

        # Touch session.updated_at so it floats to top of list
        session.updated_at = func.now()
        self.db.add(session)
        await self.db.commit()

        return ChatbotSendMessageResponse(
            user_message=ChatbotMessageRead.model_validate(user_msg),
            ai_message=ChatbotMessageRead.model_validate(ai_msg),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            model_name=model_name,
        )

    async def _call_llm(
        self,
        session: ChatbotSession,
        user_message: str,
    ):
        """Call the default LLM and return (text, input_tokens, output_tokens, cost_usd, model_name)."""
        try:
            from app.services.ai_model_cache import model_cache
            from app.services import storytelling_runtime

            ai_config = model_cache.default_generation_model
            if not ai_config:
                raise ValueError("No default AI model available")

            kernel = storytelling_runtime.kernel
            if not kernel:
                raise ValueError("AI kernel not initialised")

            history = await chatbot_crud.get_sessions(self.db, session.user_id, limit=1)
            _ = history  # not used; messages loaded below

            # Build message history from DB
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            from app.models.chatbot_message import ChatbotMessage

            result = await self.db.execute(
                select(ChatbotMessage)
                .where(ChatbotMessage.session_id == session.id)
                .order_by(ChatbotMessage.created_at)
            )
            prior_messages = result.scalars().all()

            sk_messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
            for m in prior_messages:
                sk_messages.append({"role": m.role, "content": m.content})
            sk_messages.append({"role": "user", "content": user_message})

            # Use Semantic Kernel to invoke the model
            from semantic_kernel.connectors.ai.open_ai import OpenAIChatMessageContent
            from semantic_kernel.contents import ChatHistory

            chat_history = ChatHistory()
            chat_history.add_system_message(_SYSTEM_PROMPT)
            for m in prior_messages:
                if m.role == "user":
                    chat_history.add_user_message(m.content)
                else:
                    chat_history.add_assistant_message(m.content)
            chat_history.add_user_message(user_message)

            chat_service = kernel.get_service(ai_config.model_name)
            result_content = await chat_service.get_chat_message_contents(
                chat_history=chat_history,
                settings=chat_service.get_prompt_execution_settings_class()()
            )

            response_text = str(result_content[0]) if result_content else ""
            usage = getattr(result_content[0], "metadata", {}).get("usage", None) if result_content else None
            input_tokens = getattr(usage, "prompt_tokens", None) if usage else None
            output_tokens = getattr(usage, "completion_tokens", None) if usage else None
            cost_usd = None
            if input_tokens and output_tokens:
                cost_usd = round((input_tokens * 0.000001 + output_tokens * 0.000002), 6)

            return response_text, input_tokens, output_tokens, cost_usd, ai_config.model_name

        except Exception as exc:
            logger.error("Chatbot LLM call failed: %s", exc, exc_info=True)
            fallback = (
                "I'm having trouble reaching the AI right now. "
                "Please try again in a moment."
            )
            return fallback, None, None, None, None
