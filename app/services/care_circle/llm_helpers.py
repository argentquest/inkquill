"""
LLM helper functions for Care Circle providers.

Bypasses the model cache and builds clients directly from Care Circle
environment settings so providers can cleanly fall back when a given
provider is unavailable.
"""

from __future__ import annotations

import datetime
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Tuple
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)

_DEMENTIA_SYSTEM_PROMPT_BASE = (
    "You are a kind, warm, and patient assistant creating daily content for older adults, "
    "some of whom are living with dementia. "
    "Use simple, clear language. Keep responses short and positive. "
    "Avoid anything confusing, distressing, or that tests memory. "
    "Focus on familiar, comforting, and uplifting topics."
)

# Static constant kept for backwards compatibility — new code should use
# get_dementia_system_prompt() so the date is injected automatically.
DEMENTIA_SYSTEM_PROMPT = _DEMENTIA_SYSTEM_PROMPT_BASE


def get_dementia_system_prompt(for_date: datetime.date) -> str:
    """Return the dementia system prompt with today's date injected."""
    date_str = f"{for_date.strftime('%B')} {for_date.day}, {for_date.year}"
    return f"{_DEMENTIA_SYSTEM_PROMPT_BASE} Today's date is {date_str}."


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""


def _normalize_provider_name(value: str | None, default: str = "AUTO") -> str:
    return str(value or default).strip().upper()


def _normalize_azure_foundry_endpoint(endpoint: str) -> str:
    trimmed = endpoint.strip().rstrip("/")
    parsed = urlparse(trimmed)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError("AZURE_FOUNDRY_ENDPOINT must be a valid HTTPS URL.")
    return f"{parsed.scheme}://{parsed.netloc}"


def _build_azure_foundry_client(model_name: str):
    import openai
    from app.core.config import settings

    if not settings.AZURE_FOUNDRY_API_KEY:
        raise RuntimeError("AZURE_FOUNDRY_API_KEY is not configured.")
    if not settings.AZURE_FOUNDRY_ENDPOINT:
        raise RuntimeError("AZURE_FOUNDRY_ENDPOINT is not configured.")

    client = openai.AsyncAzureOpenAI(
        api_key=settings.AZURE_FOUNDRY_API_KEY,
        azure_endpoint=_normalize_azure_foundry_endpoint(settings.AZURE_FOUNDRY_ENDPOINT),
        api_version=settings.AZURE_FOUNDRY_API_VERSION,
    )
    return client, model_name


def _build_text_client():
    """Return (client, model_name) for Care Circle text generation."""
    import openai
    from app.core.config import settings

    provider = _normalize_provider_name(settings.CARE_CIRCLE_TEXT_PROVIDER)

    if provider == "AZURE_FOUNDRY":
        model_name = (
            settings.AZURE_FOUNDRY_TEXT_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_TEXT_MODEL
        )
        return _build_azure_foundry_client(model_name)

    if provider in {"LMSTUDIO", "AUTO"} and settings.LMSTUDIO_ENABLED:
        client = openai.AsyncOpenAI(
            api_key="lm-studio",
            base_url=settings.LMSTUDIO_BASE_URL,
        )
        return client, settings.LMSTUDIO_MODEL

    if provider in {"OPENROUTER", "AUTO"} and settings.OPENROUTER_API_KEY:
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

    if provider in {"OPENAI", "AUTO"} and settings.OPENAI_API_KEY:
        model_name = "gpt-4o-mini"
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return client, model_name

    if (
        provider == "AUTO"
        and settings.AZURE_FOUNDRY_API_KEY
        and settings.AZURE_FOUNDRY_ENDPOINT
    ):
        model_name = (
            settings.AZURE_FOUNDRY_TEXT_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_TEXT_MODEL
        )
        return _build_azure_foundry_client(model_name)

    raise RuntimeError(
        "No Care Circle text provider is configured. Set CARE_CIRCLE_TEXT_PROVIDER with matching credentials."
    )


def _build_image_client():
    """Return (client, model_name) for Care Circle image generation."""
    import openai
    from app.core.config import settings

    provider = _normalize_provider_name(settings.CARE_CIRCLE_IMAGE_PROVIDER)

    if provider == "AZURE_FOUNDRY":
        model_name = (
            settings.AZURE_FOUNDRY_IMAGE_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_IMAGE_MODEL
        )
        return _build_azure_foundry_client(model_name)

    if provider in {"OPENAI", "AUTO"} and settings.OPENAI_API_KEY:
        return (
            openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY),
            settings.OPENAI_IMAGE_MODEL,
        )

    if (
        provider == "AUTO"
        and settings.AZURE_FOUNDRY_API_KEY
        and settings.AZURE_FOUNDRY_ENDPOINT
    ):
        model_name = (
            settings.AZURE_FOUNDRY_IMAGE_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_IMAGE_MODEL
        )
        return _build_azure_foundry_client(model_name)

    raise RuntimeError(
        "No Care Circle image provider is configured. Set CARE_CIRCLE_IMAGE_PROVIDER with matching credentials."
    )


async def generate_text_with_usage(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 4096,
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
    max_tokens: int = 4096,
    temperature: float = 0.9,
) -> Tuple[dict[str, Any], LLMResponse]:
    """Call the LLM, parse JSON from the response, return (dict, LLMResponse)."""
    llm_response = await generate_text_with_usage(
        prompt,
        system=system,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    raw = llm_response.content.strip()
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


_OPENAI_ONLY_PARAMS = {"openai/", "gpt-image", "dall-e"}


async def generate_image_url_with_usage(prompt: str) -> LLMResponse:
    """Generate an image and return an LLMResponse whose `.content` is a URL or data URI."""
    client, model_name = _build_image_client()

    is_openai_model = any(token in model_name for token in _OPENAI_ONLY_PARAMS)
    kwargs: dict[str, Any] = {"model": model_name, "prompt": prompt, "n": 1}
    if is_openai_model:
        kwargs["size"] = "1024x1024"
        kwargs["quality"] = "low"

    response = await client.images.generate(**kwargs)
    item = response.data[0]

    image_url: str = item.url or ""
    if not image_url and item.b64_json:
        image_url = f"data:image/png;base64,{item.b64_json}"

    if not image_url:
        raise RuntimeError("Image generation returned no URL or base64 data.")

    return LLMResponse(content=image_url, model=model_name)
