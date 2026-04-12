"""
LLM helper functions for Care Circle providers.

Bypasses the model_cache (which requires DB records) and builds clients
directly from env settings. Falls back gracefully so providers can serve
their static fallback content when no API key is configured.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Tuple

logger = logging.getLogger(__name__)

DEMENTIA_SYSTEM_PROMPT = (
    "You are a kind, warm, and patient assistant creating daily content for older adults, "
    "some of whom are living with dementia. "
    "Use simple, clear language. Keep responses short and positive. "
    "Avoid anything confusing, distressing, or that tests memory. "
    "Focus on familiar, comforting, and uplifting topics."
)


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""


def _build_text_client():
    """Return (AsyncOpenAI client, model_name) for text generation.

    Priority: LM Studio (local) → OpenRouter → OpenAI fallback.
    """
    import openai
    from app.core.config import settings

    if settings.LMSTUDIO_ENABLED:
        client = openai.AsyncOpenAI(
            api_key="lm-studio",  # LM Studio doesn't validate the key
            base_url=settings.LMSTUDIO_BASE_URL,
        )
        return client, settings.LMSTUDIO_MODEL

    if settings.OPENROUTER_API_KEY:
        model_name = settings.CARE_CIRCLE_DEFAULT_TEXT_MODEL
        default_headers: dict[str, str] = {}
        if settings.OPENROUTER_SITE_URL:
            default_headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            default_headers["X-Title"] = settings.OPENROUTER_APP_NAME
        client = openai.AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers=default_headers or None,
        )
        return client, model_name

    if settings.OPENAI_API_KEY:
        model_name = "gpt-4o-mini"
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return client, model_name

    raise RuntimeError(
        "No LLM API key configured. Set OPENROUTER_API_KEY or OPENAI_API_KEY in .env."
    )


def _build_image_client():
    """Return (AsyncOpenAI client, model_name) for image generation.

    Uses the standard OpenAI API (DALL-E / gpt-image-1) or OpenRouter.
    """
    import openai
    from app.core.config import settings

    if settings.OPENAI_API_KEY:
        return openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY), settings.OPENAI_IMAGE_MODEL

    if settings.OPENROUTER_API_KEY:
        default_headers: dict[str, str] = {}
        if settings.OPENROUTER_SITE_URL:
            default_headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            default_headers["X-Title"] = settings.OPENROUTER_APP_NAME
        client = openai.AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers=default_headers or None,
        )
        return client, settings.CARE_CIRCLE_DEFAULT_IMAGE_MODEL

    raise RuntimeError(
        "No image API key configured. Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env."
    )


async def generate_text_with_usage(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 512,
    temperature: float = 0.9,
) -> LLMResponse:
    """Call the LLM and return an LLMResponse whose `.content` is the text reply."""
    client, model_name = _build_text_client()

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    content = (response.choices[0].message.content or "").strip()
    usage = response.usage
    return LLMResponse(
        content=content,
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
        total_tokens=usage.total_tokens if usage else 0,
        model=model_name,
    )


async def generate_json_with_usage(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.9,
) -> Tuple[dict[str, Any], LLMResponse]:
    """Call the LLM, parse JSON from the response, return (dict, LLMResponse).

    Strips markdown code fences before parsing. Returns ({}, response) if JSON
    cannot be extracted so providers can serve their fallback.
    """
    llm_response = await generate_text_with_usage(
        prompt, system=system, max_tokens=max_tokens, temperature=temperature
    )

    raw = llm_response.content.strip()

    # Strip markdown code fences: ```json ... ``` or ``` ... ```
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw.strip())

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    return data, llm_response


async def generate_image_url_with_usage(prompt: str) -> LLMResponse:
    """Generate an image and return an LLMResponse whose `.content` is a URL or data URI."""
    client, model_name = _build_image_client()

    response = await client.images.generate(
        model=model_name,
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="low",
    )
    item = response.data[0]

    # Prefer a direct URL if the model returns one
    image_url: str = item.url or ""

    # Some models (e.g. gpt-image-1) return base64 instead of a URL
    if not image_url and item.b64_json:
        image_url = f"data:image/png;base64,{item.b64_json}"

    if not image_url:
        raise RuntimeError("Image generation returned no URL or base64 data.")

    return LLMResponse(content=image_url, model=model_name)
