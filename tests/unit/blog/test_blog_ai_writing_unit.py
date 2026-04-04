"""Mock-based unit tests for blog AI writing async handlers."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.routers import blog_ai_writing as blog_ai


pytestmark = pytest.mark.unit


def _user():
    return SimpleNamespace(id=1, username="unit_user")


@pytest.mark.asyncio
async def test_handle_generate_content_success_with_world_context(mock_db_session):
    """Generate-content handler should send thinking + content_generated on success."""
    send_mock = AsyncMock()
    fake_model = SimpleNamespace(max_tokens=1024, temperature=0.7, top_p=1.0)
    fake_function = SimpleNamespace(invoke=AsyncMock(return_value=SimpleNamespace(value="Generated blog content")))
    fake_kernel = SimpleNamespace(plugins={})

    with patch.object(blog_ai.blog_writing_manager, "send_message", send_mock), patch.object(
        blog_ai, "model_cache", SimpleNamespace(default_generation_model=fake_model)
    ), patch.object(
        blog_ai,
        "BlogPromptService",
        SimpleNamespace(format_content_generation_prompt=lambda **kwargs: "prompt-content"),
    ), patch.object(blog_ai, "build_document_context", new=AsyncMock(return_value=("doc ctx", []))), patch.object(
        blog_ai, "generate_act_narrative_only_function", fake_function
    ), patch.object(blog_ai, "kernel", fake_kernel), patch.object(
        blog_ai, "log_ai_streaming_call", new=AsyncMock()
    ):
        await blog_ai.handle_generate_content(
            "s1",
            {"topic": "Worldbuilding", "style": "informative", "use_world_context": True, "world_id": 10},
            _user(),
            mock_db_session,
        )

    assert send_mock.await_count >= 2
    sent_types = [call.args[1]["type"] for call in send_mock.await_args_list]
    assert "thinking" in sent_types
    assert "content_generated" in sent_types


@pytest.mark.asyncio
async def test_handle_improve_writing_success(mock_db_session):
    """Improve-writing handler should send content_improved on success."""
    send_mock = AsyncMock()
    fake_model = SimpleNamespace(max_tokens=1024, temperature=0.7, top_p=1.0)
    fake_function = SimpleNamespace(invoke=AsyncMock(return_value=SimpleNamespace(value="Improved content")))
    fake_kernel = SimpleNamespace(plugins={})

    with patch.object(blog_ai.blog_writing_manager, "send_message", send_mock), patch.object(
        blog_ai, "model_cache", SimpleNamespace(default_generation_model=fake_model)
    ), patch.object(
        blog_ai,
        "BlogPromptService",
        SimpleNamespace(format_improve_writing_prompt=lambda **kwargs: "prompt-improve"),
    ), patch.object(blog_ai, "generate_act_narrative_only_function", fake_function), patch.object(
        blog_ai, "kernel", fake_kernel
    ), patch.object(blog_ai, "log_ai_streaming_call", new=AsyncMock()):
        await blog_ai.handle_improve_writing(
            "s2",
            {"content": "draft blog", "improvement_type": "clarity"},
            _user(),
            mock_db_session,
        )

    sent_types = [call.args[1]["type"] for call in send_mock.await_args_list]
    assert "content_improved" in sent_types


@pytest.mark.asyncio
async def test_handle_generate_title_success(mock_db_session):
    """Generate-title handler should parse titles and send titles_generated."""
    send_mock = AsyncMock()
    fake_model = SimpleNamespace(max_tokens=1024, temperature=0.7, top_p=1.0)
    fake_function = SimpleNamespace(
        invoke=AsyncMock(return_value=SimpleNamespace(value="1. First Title\n2. Second Title"))
    )
    fake_kernel = SimpleNamespace(plugins={})

    with patch.object(blog_ai.blog_writing_manager, "send_message", send_mock), patch.object(
        blog_ai, "model_cache", SimpleNamespace(default_generation_model=fake_model)
    ), patch.object(
        blog_ai,
        "BlogPromptService",
        SimpleNamespace(format_generate_title_prompt=lambda **kwargs: "prompt-title"),
    ), patch.object(blog_ai, "generate_act_narrative_only_function", fake_function), patch.object(
        blog_ai, "kernel", fake_kernel
    ), patch.object(blog_ai, "log_ai_streaming_call", new=AsyncMock()):
        await blog_ai.handle_generate_title(
            "s3",
            {"content": "blog body", "topic": "AI", "style": "engaging"},
            _user(),
            mock_db_session,
        )

    title_payloads = [call.args[1] for call in send_mock.await_args_list if call.args[1]["type"] == "titles_generated"]
    assert title_payloads
    assert "First Title" in title_payloads[0]["titles"][0]


@pytest.mark.asyncio
async def test_handle_generate_excerpt_and_tips_success(mock_db_session):
    """Generate-excerpt and writing-tips handlers should send expected message types."""
    send_mock = AsyncMock()
    fake_model = SimpleNamespace(max_tokens=1024, temperature=0.7, top_p=1.0)
    fake_function = SimpleNamespace(invoke=AsyncMock(return_value=SimpleNamespace(value="Excerpt or tips output")))
    fake_kernel = SimpleNamespace(plugins={})

    with patch.object(blog_ai.blog_writing_manager, "send_message", send_mock), patch.object(
        blog_ai, "model_cache", SimpleNamespace(default_generation_model=fake_model)
    ), patch.object(
        blog_ai,
        "BlogPromptService",
        SimpleNamespace(
            format_generate_excerpt_prompt=lambda content, max_length=200: "prompt-excerpt",
            format_writing_tips_prompt=lambda **kwargs: "prompt-tips",
        ),
    ), patch.object(blog_ai, "generate_act_narrative_only_function", fake_function), patch.object(
        blog_ai, "kernel", fake_kernel
    ), patch.object(blog_ai, "log_ai_streaming_call", new=AsyncMock()):
        await blog_ai.handle_generate_excerpt("s4", {"content": "body text"}, _user(), mock_db_session)
        await blog_ai.handle_get_writing_tips("s4", {"content": "body text", "tip_type": "seo"}, _user(), mock_db_session)

    sent_types = [call.args[1]["type"] for call in send_mock.await_args_list]
    assert "excerpt_generated" in sent_types
    assert "writing_tips" in sent_types


@pytest.mark.asyncio
async def test_handle_suggest_tags_success(mock_db_session):
    """Suggest-tags handler should parse comma-separated tag output and return tags_suggested."""
    send_mock = AsyncMock()
    fake_function = SimpleNamespace(invoke=AsyncMock(return_value=SimpleNamespace(value="ai, writing, storytelling")))
    fake_kernel = SimpleNamespace(plugins={})

    mock_db_session.execute = AsyncMock(return_value=SimpleNamespace(fetchall=lambda: [("ai",), ("writing",)]))

    with patch.object(blog_ai.blog_writing_manager, "send_message", send_mock), patch.object(
        blog_ai,
        "BlogPromptService",
        SimpleNamespace(format_suggest_tags_prompt=lambda **kwargs: "prompt-tags"),
    ), patch.object(blog_ai, "generate_act_narrative_only_function", fake_function), patch.object(
        blog_ai, "kernel", fake_kernel
    ):
        await blog_ai.handle_suggest_tags("s5", {"content": "blog body", "title": "post"}, _user(), mock_db_session)

    tag_payloads = [call.args[1] for call in send_mock.await_args_list if call.args[1]["type"] == "tags_suggested"]
    assert tag_payloads
    assert "ai" in tag_payloads[0]["suggested_tags"]

