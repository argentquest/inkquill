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

# Stage to cognitive level mapping
# "early" (early/very mild) → Level 4 (least restrictive)
# "mild" → Level 3
# "moderate" → Level 2
# "severe" (advanced) → Level 1 (most restrictive)
_STAGE_TO_LEVEL = {
    "early": 4,
    "mild": 3,
    "moderate": 2,
    "severe": 1,
}

# Legacy constant kept for backwards compatibility
_DEMENTIA_SYSTEM_PROMPT_BASE = (
    "You are a kind, warm, and patient assistant creating daily content for older adults, "
    "some of whom are living with dementia. "
    "Use simple, clear language. Keep responses short and positive. "
    "Avoid anything confusing, distressing, or that tests memory. "
    "Focus on familiar, comforting, and uplifting topics."
)

DEMENTIA_SYSTEM_PROMPT = _DEMENTIA_SYSTEM_PROMPT_BASE


_ENHANCED_DEMENTIA_SYSTEM_PROMPT_TEMPLATE = """You are a kind, warm, and patient assistant creating daily newsletter content
for older adults, some of whom are living with cognitive decline.

Your primary goal is to help the reader feel safe, calm, valued,
and emotionally supported.

--------------------------------
COGNITIVE LEVEL CONFIGURATION
--------------------------------
COGNITIVE_LEVEL = {cognitive_level}
Patient cognitive stage: {patient_stage}
Today's date: {date_str}

Adjust language complexity, length, structure, and detail strictly
according to the selected cognitive level.

--------------------------------
GLOBAL RULES (ALL LEVELS)
--------------------------------
- Maintain a calm, reassuring, and positive tone
- Use familiar, comforting, and uplifting topics only
- Do NOT test memory or require recall
- Do NOT reference illness, dementia, decline, or loss
- Avoid distressing, urgent, negative, or surprising content
- Avoid complex explanations or abstract concepts beyond the allowed level
- Use a consistent structure:
  Greeting → Body → Closing

--------------------------------
LEVEL-SPECIFIC OUTPUT RULES
--------------------------------

LEVEL 1 (Advanced Cognitive Decline):
- Word count: 30–50 words
- Paragraphs: 1
- Sentence length: max 10 words
- One idea only
- Extremely simple language
- No questions of any kind

LEVEL 2 (Moderate Cognitive Decline):
- Word count: 50–80 words
- Paragraphs: 1–2
- Sentence length: max 14 words
- Very simple, clear language
- No memory-based or reflective questions

LEVEL 3 (Mild Cognitive Decline):
- Word count: 80–130 words
- Paragraphs: 2–3
- Sentence length: max 18 words
- Clear and friendly language
- Gentle reflection allowed
- No memory recall or testing questions

LEVEL 4 (Very Mild / Early Decline):
- Word count: 130–200 words
- Paragraphs: 3–4 short paragraphs
- Sentence length: max 22 words
- Natural, easy-to-follow language
- Gentle descriptive complexity allowed
- Maintain emotional safety at all times

--------------------------------
RESTRICTED VOCABULARY (ALL LEVELS)
--------------------------------
Do NOT use or reference:
- Medical or decline terms:
  dementia, alzheimer's, illness, disease, condition, symptoms,
  diagnosis, treatment, medication, memory loss
- Memory testing or time recall language:
  remember, recall, think back, yesterday, last week, years ago,
  when you were, in the past
- Distressing language:
  sad, lonely, afraid, worried, grief, loss, death, dying, emergency

--------------------------------
CONTENT STRUCTURE
--------------------------------
Always follow this structure:

1. Greeting:
   A warm, friendly opening sentence.

2. Body:
   Content adjusted to cognitive level.
   Familiar, comforting, and positive ideas only.

3. Closing:
   A gentle, reassuring closing sentence or paragraph.

--------------------------------
AUTOMATED SELF-QA (MANDATORY)
--------------------------------
Before producing the final output, you must verify:

1. Word count is within the allowed range for the cognitive level
2. Paragraph count matches the allowed range
3. No sentence exceeds the maximum length
4. No restricted vocabulary is present
5. No memory-testing or recall-based questions are included
6. Structure follows Greeting → Body → Closing
7. Tone is calm, positive, and reassuring

If ANY rule is violated:
- Revise the content
- Re-check all rules
- Repeat until all checks pass

Only output the final, corrected newsletter content.
Do not explain the QA process in the final answer."""


def get_dementia_system_prompt(for_date: datetime.date) -> str:
    """Return the legacy dementia system prompt with today's date injected."""
    date_str = f"{for_date.strftime('%B')} {for_date.day}, {for_date.year}"
    return f"{_DEMENTIA_SYSTEM_PROMPT_BASE} Today's date is {date_str}."


def get_enhanced_dementia_system_prompt(
    patient_stage: str, for_date: datetime.date
) -> str:
    """Return the enhanced dementia system prompt with cognitive level and date injected.
    
    Args:
        patient_stage: Patient's cognitive stage ("early", "mild", "moderate", "severe")
        for_date: Date to inject into the prompt
    
    Returns:
        Complete system prompt with cognitive level and date configured
    """
    cognitive_level = _STAGE_TO_LEVEL.get(patient_stage.lower(), 2)  # Default to Level 2 (moderate)
    date_str = f"{for_date.strftime('%B')} {for_date.day}, {for_date.year}"
    
    return _ENHANCED_DEMENTIA_SYSTEM_PROMPT_TEMPLATE.format(
        cognitive_level=cognitive_level,
        patient_stage=patient_stage,
        date_str=date_str,
    )


_GENERAL_SYSTEM_PROMPT_TEMPLATE = """You are a warm, thoughtful assistant creating personalised daily content for adults.

Your goal is to delight, inform, and uplift the reader with content that feels like it was crafted just for them.

Today's date: {date_str}

--------------------------------
TONE & STYLE
--------------------------------
- Conversational, warm, and genuine — like a letter from a good friend
- Positive and uplifting without being saccharine
- Natural prose: no artificial simplification of vocabulary or sentence length
- Personalised: weave in the reader's name, interests, and background where relevant

--------------------------------
CONTENT GUIDELINES
--------------------------------
- Focus on topics the reader enjoys: hobbies, interests, nostalgia, nature, humour
- Feel free to be a little witty or playful where appropriate
- You may reference the past (memories, history, "back in the day") naturally
- Appropriate length: write as much as the content naturally needs — not too short, not padded
- No need to restrict vocabulary, sentence length, or paragraph count

--------------------------------
WHAT TO AVOID
--------------------------------
- Medical, clinical, or care-facility language
- Anything patronising, infantilising, or condescending
- Excessive repetition or padding
- Overly formal or stiff language

Only output the final content. Do not include meta-commentary about the content."""


def get_general_system_prompt(for_date: datetime.date) -> str:
    """Return the general-population system prompt with today's date injected."""
    date_str = f"{for_date.strftime('%B')} {for_date.day}, {for_date.year}"
    return _GENERAL_SYSTEM_PROMPT_TEMPLATE.format(date_str=date_str)


def get_care_mode_system_prompt(care_mode: str, patient_stage: str, for_date: datetime.date) -> str:
    """Return the appropriate system prompt based on the patient's care_mode.

    Args:
        care_mode: "memory_care" or "general"
        patient_stage: Patient's cognitive stage (only used for memory_care)
        for_date: Date to inject into the prompt
    """
    if care_mode == "general":
        return get_general_system_prompt(for_date)
    return get_dementia_system_prompt(for_date)


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""


def _normalize_provider_name(value: str | None, default: str = "AUTO") -> str:
    return str(value or default).strip().upper()


def _normalize_azure_foundry_endpoint(endpoint: str, setting_name: str = "AZURE_FOUNDRY_ENDPOINT") -> str:
    trimmed = endpoint.strip().rstrip("/")
    parsed = urlparse(trimmed)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError(f"{setting_name} must be a valid HTTPS URL.")
    return trimmed


def _build_foundry_openai_base_url(endpoint: str) -> str:
    return f"{endpoint.rstrip('/')}/openai/v1/"


def _build_azure_foundry_client(model_name: str, endpoint: str):
    import openai

    if not settings.AZURE_FOUNDRY_API_KEY:
        raise RuntimeError("AZURE_FOUNDRY_API_KEY is not configured.")
    parsed = urlparse(endpoint)

    # Azure AI Foundry project/resource endpoints on services.ai.azure.com use
    # the OpenAI-compatible v1 base_url flow, including non-OpenAI models like Grok.
    if parsed.netloc.endswith("services.ai.azure.com"):
        client = openai.AsyncOpenAI(
            api_key=settings.AZURE_FOUNDRY_API_KEY,
            base_url=_build_foundry_openai_base_url(endpoint),
        )
        return client, model_name

    client = openai.AsyncAzureOpenAI(
        api_key=settings.AZURE_FOUNDRY_API_KEY,
        azure_endpoint=f"{parsed.scheme}://{parsed.netloc}",
        api_version=settings.AZURE_FOUNDRY_API_VERSION,
    )
    return client, model_name


def _build_text_client():
    """Return (client, model_name) for Care Circle text generation."""
    import openai
    from app.core.config import settings

    provider = _normalize_provider_name(settings.CARE_CIRCLE_TEXT_PROVIDER)

    if provider == "AZURE_FOUNDRY":
        endpoint_value = (
            settings.AZURE_FOUNDRY_TEXT_ENDPOINT
            or settings.AZURE_FOUNDRY_ENDPOINT
        )
        if not endpoint_value:
            raise RuntimeError("AZURE_FOUNDRY_TEXT_ENDPOINT or AZURE_FOUNDRY_ENDPOINT is not configured.")
        endpoint = _normalize_azure_foundry_endpoint(endpoint_value, "AZURE_FOUNDRY_TEXT_ENDPOINT")
        model_name = (
            settings.AZURE_FOUNDRY_TEXT_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_TEXT_MODEL
        )
        return _build_azure_foundry_client(model_name, endpoint)

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
        model_name = settings.DEFAULT_GENERATION_MODEL_NAME
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return client, model_name

    if (
        provider == "AUTO"
        and settings.AZURE_FOUNDRY_API_KEY
        and (settings.AZURE_FOUNDRY_TEXT_ENDPOINT or settings.AZURE_FOUNDRY_ENDPOINT)
    ):
        endpoint = _normalize_azure_foundry_endpoint(
            settings.AZURE_FOUNDRY_TEXT_ENDPOINT or settings.AZURE_FOUNDRY_ENDPOINT,
            "AZURE_FOUNDRY_TEXT_ENDPOINT",
        )
        model_name = (
            settings.AZURE_FOUNDRY_TEXT_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_TEXT_MODEL
        )
        return _build_azure_foundry_client(model_name, endpoint)

    raise RuntimeError(
        "No Care Circle text provider is configured. Set CARE_CIRCLE_TEXT_PROVIDER with matching credentials."
    )


def _build_image_client():
    """Return (client, model_name) for Care Circle image generation."""
    import openai
    from app.core.config import settings

    provider = _normalize_provider_name(settings.CARE_CIRCLE_IMAGE_PROVIDER)

    if provider == "AZURE_FOUNDRY":
        endpoint_value = (
            settings.AZURE_FOUNDRY_IMAGE_ENDPOINT
            or settings.AZURE_FOUNDRY_ENDPOINT
        )
        if not endpoint_value:
            raise RuntimeError("AZURE_FOUNDRY_IMAGE_ENDPOINT or AZURE_FOUNDRY_ENDPOINT is not configured.")
        endpoint = _normalize_azure_foundry_endpoint(endpoint_value, "AZURE_FOUNDRY_IMAGE_ENDPOINT")
        model_name = (
            settings.AZURE_FOUNDRY_IMAGE_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_IMAGE_MODEL
        )
        return _build_azure_foundry_client(model_name, endpoint)

    if provider in {"OPENAI", "AUTO"} and settings.OPENAI_API_KEY:
        return (
            openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY),
            settings.OPENAI_IMAGE_MODEL,
        )

    if (
        provider == "AUTO"
        and settings.AZURE_FOUNDRY_API_KEY
        and (settings.AZURE_FOUNDRY_IMAGE_ENDPOINT or settings.AZURE_FOUNDRY_ENDPOINT)
    ):
        endpoint = _normalize_azure_foundry_endpoint(
            settings.AZURE_FOUNDRY_IMAGE_ENDPOINT or settings.AZURE_FOUNDRY_ENDPOINT,
            "AZURE_FOUNDRY_IMAGE_ENDPOINT",
        )
        model_name = (
            settings.AZURE_FOUNDRY_IMAGE_DEPLOYMENT
            or settings.CARE_CIRCLE_DEFAULT_IMAGE_MODEL
        )
        return _build_azure_foundry_client(model_name, endpoint)

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
