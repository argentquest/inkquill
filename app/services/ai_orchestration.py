"""AI orchestration backend selection and capability checks."""

from __future__ import annotations

import importlib.util
import logging
from typing import Dict

from app.core.config import settings

logger = logging.getLogger(__name__)

SEMANTIC_KERNEL_BACKEND = "SEMANTIC_KERNEL"
LANGGRAPH_BACKEND = "LANGGRAPH"


def get_ai_orchestration_backend() -> str:
    """Return the configured orchestration backend in normalized form."""
    return (settings.AI_ORCHESTRATION_BACKEND or LANGGRAPH_BACKEND).strip().upper()


def orchestration_backend_is_semantic_kernel() -> bool:
    """Return whether Semantic Kernel is the active orchestration backend."""
    return get_ai_orchestration_backend() == SEMANTIC_KERNEL_BACKEND


def orchestration_backend_is_langgraph() -> bool:
    """Return whether LangGraph is the active orchestration backend."""
    return get_ai_orchestration_backend() == LANGGRAPH_BACKEND


def detect_optional_backends() -> Dict[str, bool]:
    """Check whether optional orchestration packages are importable."""
    return {
        "semantic_kernel": importlib.util.find_spec("semantic_kernel") is not None,
        "langchain": importlib.util.find_spec("langchain") is not None,
        "langgraph": importlib.util.find_spec("langgraph") is not None,
        "langchain_openai": importlib.util.find_spec("langchain_openai") is not None,
    }


def log_orchestration_configuration() -> None:
    """Log the configured backend and detected optional dependencies."""
    backend = get_ai_orchestration_backend()
    availability = detect_optional_backends()
    logger.info("AI orchestration backend configured as '%s'", backend)
    logger.info("AI orchestration package availability: %s", availability)
