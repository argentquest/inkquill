"""Service helpers for direct context."""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage_deps import resolve_storage_path, build_storage_url
from app.crud import document as crud_document
from app.models.uploaded_document import UploadedDocument

logger = logging.getLogger(__name__)


def _clip_text(text: str, max_chars: int) -> str:
    """Provide service support for clip text."""
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _tokenize_query(query: str) -> List[str]:
    """Provide service support for tokenize query."""
    return [term for term in re.findall(r"[a-zA-Z0-9]{4,}", (query or "").lower())]


def _score_document(text: str, query_terms: List[str]) -> int:
    """Provide service support for score document."""
    haystack = (text or "").lower()
    return sum(haystack.count(term) for term in query_terms)


async def read_document_text(document: UploadedDocument) -> str:
    """Provide service support for read document text."""
    if not document.blob_storage_path:
        return ""

    extracted_path = resolve_storage_path("documents", document.blob_storage_path + ".extracted.txt")
    if extracted_path.exists():
        return extracted_path.read_text(encoding="utf-8", errors="replace")

    original_path = resolve_storage_path("documents", document.blob_storage_path)
    if original_path.suffix.lower() == ".txt" and original_path.exists():
        return original_path.read_text(encoding="utf-8", errors="replace")

    return ""


async def build_document_context(
    db: AsyncSession,
    world_id: int,
    query: str,
    *,
    max_documents: int = 3,
    max_chars_per_document: int = 1200,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Build document context."""
    documents = await crud_document.get_documents_by_world(db, world_id=world_id, skip=0, limit=25)
    if not documents:
        return "No uploaded document context available.", []

    query_terms = _tokenize_query(query)
    ranked: List[Tuple[int, UploadedDocument, str]] = []
    for document in documents:
        text = await read_document_text(document)
        if not text:
            continue
        ranked.append((_score_document(text, query_terms), document, text))

    if not ranked:
        return "No extracted document text available.", []

    ranked.sort(key=lambda item: (item[0], item[1].uploaded_at), reverse=True)
    selected = ranked[:max_documents]

    context_parts: List[str] = []
    sources: List[Dict[str, Any]] = []
    for _, document, text in selected:
        excerpt = _clip_text(text, max_chars_per_document)
        context_parts.append(f"[{document.filename}]\n{excerpt}")
        sources.append(
            {
                "filename": document.filename,
                "document_id": document.id,
                "preview": _clip_text(text, 160),
                "link": build_storage_url("documents", document.blob_storage_path),
                "type": "document",
            }
        )

    return "\n\n".join(context_parts), sources


def build_structured_world_context(world_context: Any, *, max_items_per_group: int = 8) -> str:
    """Build structured world context."""
    def _lines(items: List[Dict[str, Any]], name_key: str, extra_keys: List[str]) -> List[str]:
        lines: List[str] = []
        for item in items[:max_items_per_group]:
            name = item.get(name_key) or item.get("title") or "Untitled"
            details = [str(item.get(key)).strip() for key in extra_keys if item.get(key)]
            snippet = " | ".join(details[:2])
            lines.append(f"- {name}" + (f": {snippet}" if snippet else ""))
        if len(items) > max_items_per_group:
            lines.append(f"- ...and {len(items) - max_items_per_group} more")
        return lines or ["- None"]

    parts = [
        f"WORLD: {world_context.world.get('name', 'Unknown')}",
        f"Description: {world_context.world.get('description', 'No description')}",
        "",
        "CHARACTERS:",
        * _lines(world_context.characters, "name", ["description", "personality_traits", "backstory"]),
        "",
        "LOCATIONS:",
        * _lines(world_context.locations, "name", ["description", "atmosphere", "significance"]),
        "",
        "LORE ITEMS:",
        * _lines(world_context.lore_items, "title", ["description", "category"]),
        "",
        "STORIES:",
        * _lines(world_context.stories, "title", ["short_description"]),
        "",
        "ACTS:",
        * _lines(world_context.acts, "title", ["act_summary", "description"]),
        "",
        "SCENES:",
        * _lines(world_context.scenes, "title", ["summary", "mood"]),
    ]
    return "\n".join(parts)
