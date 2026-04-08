"""LangGraph-backed compatibility runtime for legacy prompt functions."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, AsyncIterator, Dict, Iterable, Optional, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class PromptState(TypedDict, total=False):
    """State object carried through the one-step LangGraph runtime."""

    prompt: str
    execution_settings: "OpenAIChatPromptExecutionSettings"
    content: str
    metadata: dict[str, Any]


def _serialize_prompt_value(value: Any) -> str:
    """Serialize prompt inputs into strings the templates can consume."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, (dict, list, tuple, set)):
        try:
            return json.dumps(value, ensure_ascii=False, indent=2)
        except TypeError:
            return str(value)
    return str(value)


def render_semantic_kernel_template(template: str, variables: Dict[str, Any]) -> str:
    """Render the subset of Semantic Kernel template syntax used in this repo."""

    rendered = template
    for key, value in variables.items():
        string_value = _serialize_prompt_value(value)
        rendered = rendered.replace("{{$" + key + "}}", string_value)
        rendered = rendered.replace(f"{{{{${key}}}}}", string_value)
        rendered = rendered.replace(f"{{{{{key}}}}}", string_value)
    rendered = re.sub(r"\{\{\$?[\w\.]+\}\}", "", rendered)
    return rendered


@dataclass
class OpenAIChatPromptExecutionSettings:
    """Compatibility settings object mirroring legacy SK usage."""

    service_id: str = "chat_service"
    ai_model_id: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    response_format: Optional[dict[str, Any]] = None


class KernelArguments(dict):
    """Dictionary-like compatibility container for prompt arguments."""

    def __init__(
        self,
        *args: Any,
        settings: Optional[OpenAIChatPromptExecutionSettings] = None,
        execution_settings: Optional[OpenAIChatPromptExecutionSettings] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        effective_settings = settings or execution_settings
        if effective_settings is not None:
            self["settings"] = effective_settings


@dataclass
class InputVariable:
    """Compatibility container for prompt metadata."""

    name: str
    description: str = ""
    is_required: bool = True


@dataclass
class PromptTemplateConfig:
    """Compatibility prompt config used by legacy registration code."""

    template: str
    name: str
    template_format: str = "semantic-kernel"
    description: str = ""
    input_variables: list[Any] = field(default_factory=list)
    execution_settings: dict[str, OpenAIChatPromptExecutionSettings] = field(default_factory=dict)


class FunctionResult:
    """Compatibility result object with value and metadata."""

    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.value = [content]
        self.metadata = metadata or {}

    def __str__(self) -> str:
        return self.value[0] if self.value else ""


class PluginRegistry(dict):
    """Dictionary-like plugin registry with SK-style metadata helper."""

    def get_functions_metadata(self) -> list[Any]:
        return [SimpleNamespace(name=name) for name in self.keys()]


@dataclass
class PromptFunction:
    """Registered prompt function backed by LangGraph execution."""

    kernel: "LangGraphKernel"
    plugin_name: str
    function_name: str
    prompt_template_config: PromptTemplateConfig

    async def invoke(self, kernel: Optional["LangGraphKernel"] = None, arguments: Optional[dict[str, Any]] = None, **kwargs: Any) -> FunctionResult:
        runtime = kernel or self.kernel
        merged_args: dict[str, Any] = {}
        if arguments:
            merged_args.update(dict(arguments))
        merged_args.update(kwargs)
        return await runtime.invoke(self, arguments=merged_args)


class LangGraphKernel:
    """Small compatibility kernel backed by LangGraph and LangChain."""

    def __init__(self) -> None:
        self.plugins: dict[str, PluginRegistry] = {}
        self._default_service_id = "chat_service"
        self._services: dict[str, Any] = {}
        self._graph = self._build_graph()

    def add_service(self, service: Any) -> None:
        service_id = getattr(service, "service_id", self._default_service_id)
        self._default_service_id = service_id
        self._services[service_id] = service

    def get_service(self, service_id: str) -> Any:
        return self._services.get(service_id)

    def remove_service(self, service_id: str) -> None:
        self._services.pop(service_id, None)

    def add_function(self, function_name: str, plugin_name: str, prompt_template_config: PromptTemplateConfig) -> PromptFunction:
        plugin = self.plugins.setdefault(plugin_name, PluginRegistry())
        function = PromptFunction(
            kernel=self,
            plugin_name=plugin_name,
            function_name=function_name,
            prompt_template_config=prompt_template_config,
        )
        plugin[function_name] = function
        return function

    def get_function(self, plugin_name: str, function_name: str) -> Optional[PromptFunction]:
        return self.plugins.get(plugin_name, {}).get(function_name)

    async def invoke(self, function: PromptFunction, arguments: Optional[dict[str, Any]] = None, **kwargs: Any) -> FunctionResult:
        merged_args = dict(arguments or {})
        merged_args.update(kwargs)
        prompt = render_semantic_kernel_template(function.prompt_template_config.template, merged_args)
        exec_settings = merged_args.get("settings") or self._resolve_execution_settings(function.prompt_template_config)
        result = await self._graph.ainvoke(
            {
                "prompt": prompt,
                "execution_settings": exec_settings,
            }
        )
        return FunctionResult(result["content"], metadata=result["metadata"])

    async def invoke_stream(self, function: PromptFunction, arguments: Optional[dict[str, Any]] = None, **kwargs: Any) -> AsyncIterator[list[str]]:
        merged_args = dict(arguments or {})
        merged_args.update(kwargs)
        prompt = render_semantic_kernel_template(function.prompt_template_config.template, merged_args)
        exec_settings = merged_args.get("settings") or self._resolve_execution_settings(function.prompt_template_config)
        llm = self._create_llm(exec_settings)
        async for chunk in llm.astream([HumanMessage(content=prompt)]):
            text = getattr(chunk, "content", "")
            if not text:
                continue
            if isinstance(text, list):
                text = "".join(str(part) for part in text)
            yield [str(text)]

    def _resolve_execution_settings(self, prompt_template_config: PromptTemplateConfig) -> OpenAIChatPromptExecutionSettings:
        if prompt_template_config.execution_settings:
            return next(iter(prompt_template_config.execution_settings.values()))
        return OpenAIChatPromptExecutionSettings(service_id=self._default_service_id)

    def _build_graph(self):
        async def call_model(state: PromptState) -> PromptState:
            exec_settings = state["execution_settings"]
            llm = self._create_llm(exec_settings)
            response = await llm.ainvoke([HumanMessage(content=state["prompt"])])
            usage = (
                getattr(response, "usage_metadata", None)
                or response.response_metadata.get("token_usage")
                or response.response_metadata.get("usage")
                or {}
            )
            usage_dict = self._normalize_usage(usage)
            return {
                "content": response.content if isinstance(response.content, str) else str(response.content),
                "metadata": {
                    "usage": usage_dict,
                    "response_metadata": response.response_metadata,
                },
            }

        graph = StateGraph(PromptState)
        graph.add_node("call_model", call_model)
        graph.add_edge(START, "call_model")
        graph.add_edge("call_model", END)
        return graph.compile()

    def _create_llm(self, exec_settings: OpenAIChatPromptExecutionSettings) -> ChatOpenAI:
        model_name = exec_settings.ai_model_id or (
            exec_settings.service_id if exec_settings.service_id and exec_settings.service_id != "chat_service" else None
        ) or settings.DEFAULT_GENERATION_MODEL_NAME

        provider = settings.ACTIVE_LLM_PROVIDER.upper()
        common_kwargs: dict[str, Any] = {
            "model": model_name,
            "temperature": exec_settings.temperature if exec_settings.temperature is not None else 0.7,
            "max_tokens": exec_settings.max_tokens,
            "top_p": exec_settings.top_p,
            "presence_penalty": exec_settings.presence_penalty,
            "frequency_penalty": exec_settings.frequency_penalty,
        }
        if exec_settings.response_format:
            common_kwargs["model_kwargs"] = {"response_format": exec_settings.response_format}

        if provider == "OPENROUTER":
            headers = {}
            if settings.OPENROUTER_SITE_URL:
                headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
            if settings.OPENROUTER_APP_NAME:
                headers["X-Title"] = settings.OPENROUTER_APP_NAME
            return ChatOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                default_headers=headers or None,
                **common_kwargs,
            )

        if provider == "OPENAI":
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                **common_kwargs,
            )

        raise RuntimeError(f"Unsupported ACTIVE_LLM_PROVIDER '{provider}' for LangGraph kernel.")

    @staticmethod
    def _normalize_usage(raw_usage: Any) -> dict[str, int]:
        if raw_usage is None:
            return {}
        if isinstance(raw_usage, dict):
            input_tokens = raw_usage.get("input_tokens", raw_usage.get("prompt_tokens", 0))
            output_tokens = raw_usage.get("output_tokens", raw_usage.get("completion_tokens", 0))
            total_tokens = raw_usage.get("total_tokens", input_tokens + output_tokens)
            return {
                "prompt_tokens": int(input_tokens or 0),
                "completion_tokens": int(output_tokens or 0),
                "total_tokens": int(total_tokens or 0),
            }
        input_tokens = getattr(raw_usage, "input_tokens", getattr(raw_usage, "prompt_tokens", 0))
        output_tokens = getattr(raw_usage, "output_tokens", getattr(raw_usage, "completion_tokens", 0))
        total_tokens = getattr(raw_usage, "total_tokens", input_tokens + output_tokens)
        return {
            "prompt_tokens": int(input_tokens or 0),
            "completion_tokens": int(output_tokens or 0),
            "total_tokens": int(total_tokens or 0),
        }


def load_prompt_from_file(prompts_dir: str | Path, filename: str) -> str:
    """Load prompt text from disk."""
    filepath = Path(prompts_dir) / filename
    with open(filepath, "r", encoding="utf-8") as prompt_file:
        return prompt_file.read()


class OpenAIChatCompletion:
    """Compatibility stub for legacy add_service calls."""

    def __init__(self, service_id: str, ai_model_id: str, async_client: Any = None):
        self.service_id = service_id
        self.ai_model_id = ai_model_id
        self.async_client = async_client


class ServiceResponseException(Exception):
    """Compatibility exception type."""


class KernelInvokeException(Exception):
    """Compatibility exception type."""


class FunctionExecutionException(Exception):
    """Compatibility exception type."""


class ChatHistory(list):
    """Compatibility chat history container."""


def kernel_function(func):
    """No-op decorator retained for legacy imports."""
    return func
