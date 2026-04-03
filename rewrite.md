# Ink & Quill — Backend Rewrite Documentation

## Overview

This document describes the major rewrite performed on the Ink & Quill FastAPI backend. The primary goal was to **de-Azure the application** — replacing all mandatory Azure cloud dependencies with free, local, or cloud-agnostic alternatives so the app can run without any Azure subscription while keeping Azure as an optional upgrade path.

A secondary goal was to lay the groundwork for a **React SPA migration** by adding token-based authentication and standardising API response shapes.

---

## Motivation

The original codebase required several paid Azure services just to start up:

| Service | Azure Equivalent | Problem |
|---|---|---|
| LLM inference | Azure OpenAI | Requires provisioned deployment + API key |
| Embeddings | Azure OpenAI Embeddings | Same deployment, 1536-dim only |
| Vector search | Azure AI Search | Billed per index + query |
| File storage | Azure Blob Storage | Billed per GB + operations |

Any developer cloning the repo needed an active Azure subscription to run anything. The rewrite removes all of these as hard requirements.

---

## What Changed

### 1. LLM Provider — Azure OpenAI → OpenRouter

**Approach:** Added an `ACTIVE_LLM_PROVIDER` config switch (`OPENROUTER` | `OPENAI` | `AZURE`). OpenRouter is now the default — it provides access to 200+ models including free-tier ones with a single API key.

**Files changed:**
- [app/core/config.py](app/core/config.py) — Added `OPENROUTER_*` settings as primary, demoted Azure OpenAI fields to optional/legacy
- [app/services/semantic_kernel_setup.py](app/services/semantic_kernel_setup.py) — Rewrote kernel initialisation to branch on `ACTIVE_LLM_PROVIDER`, using the OpenAI connector pointed at the OpenRouter base URL for the `OPENROUTER` case
- [.env_template](.env_template) — Restructured to lead with OpenRouter configuration; Azure sections moved to clearly-marked optional blocks at the bottom

**Key design decision:** The Semantic Kernel `OpenAIChatCompletion` connector accepts a custom `base_url`, which lets us point it at OpenRouter's OpenAI-compatible endpoint. No new SDK dependency needed.

---

### 2. Embeddings — Azure OpenAI → sentence-transformers (local)

**Approach:** Replaced the `AsyncAzureOpenAI` embedding client with a local `SentenceTransformer` model. The model is downloaded from HuggingFace on first run and cached in `~/.cache/huggingface`. No API key required.

**Default model:** `all-MiniLM-L6-v2` (384-dim, ~90 MB, fast). Can be swapped for `all-mpnet-base-v2` (768-dim, more accurate) via the `LOCAL_EMBEDDING_MODEL` env var.

**Files changed:**
- [app/services/embedding_service.py](app/services/embedding_service.py) — Complete rewrite; removed `AsyncAzureOpenAI` client, replaced with lazy-loaded `SentenceTransformer`. Public function signatures (`initialize_embedding_client`, `generate_embeddings`, `close_embedding_client`) preserved for compatibility.
- [app/core/config.py](app/core/config.py) — Added `LOCAL_EMBEDDING_MODEL` (default `all-MiniLM-L6-v2`) and changed `EMBEDDING_DIMENSION` default from 1536 → 384 to match the local model
- [requirements.txt](requirements.txt) — Added `sentence-transformers==3.4.1` and `torch>=2.0.0`

**Note:** The embedding dimension change means a fresh ChromaDB collection is required if migrating from an existing Azure AI Search index. Existing indexed content needs re-ingestion.

---

### 3. Vector Database — Azure AI Search → ChromaDB (local)

**Approach:** Created a new `ContextSearchService` class backed by ChromaDB running as an embedded local database. The service exposes the same interface previously expected of `AzureAISearchService`.

**Files changed:**
- [app/services/context_search_service.py](app/services/context_search_service.py) — New file. Wraps ChromaDB with `upsert_documents`, `search`, `delete_documents_by_filter`, and `is_ready` methods.
- [app/services/context_retrieval.py](app/services/context_retrieval.py) — Rewrote `RetrievalPlugin` to query `ContextSearchService` instead of constructing an Azure `SearchClient`. Removed all Azure SDK imports. Added module-level `set_search_service` / `get_search_service` so the shared instance is injected at startup.
- [app/processing/context_ingestion.py](app/processing/context_ingestion.py) — Replaced `AzureAISearchService` usage with `ContextSearchService` obtained via `context_retrieval_module.get_search_service()`. Added `_save_to_local_storage` helper for file persistence.
- [app/processing/world_element_processor.py](app/processing/world_element_processor.py) — Updated to use the new vector service interface.
- [app/main.py](app/main.py) — Startup lifespan now initialises `ContextSearchService` and injects it via `context_retrieval_module.set_search_service(...)`.
- [requirements.txt](requirements.txt) — Added `chromadb==0.6.3`

**Data directory:** ChromaDB persists to `./data/chromadb` by default (configurable via `VECTOR_DB_PATH`).

---

### 4. File Storage — Azure Blob Storage → Local Filesystem

**Approach:** The `get_blob_service_client` FastAPI dependency now returns a `LocalStorageClient` (a simple filesystem wrapper) when `USE_AZURE_STOContextE=false` (the new default). When `USE_AZURE_STOContextE=true`, it lazily imports the Azure SDK and yields a real `BlobServiceClient`.

**Files changed:**
- [app/core/azure_deps.py](app/core/azure_deps.py) — Complete rewrite. Added `LocalStorageClient` class with async `upload_blob` / `delete_blob` / `close` methods. The dependency function branches on `settings.USE_AZURE_STOContextE`; Azure SDK imports are inside the `if` branch so they are never evaluated when Azure is disabled.
- [app/services/azure_blob_service.py](app/services/azure_blob_service.py) — Updated to use lazy Azure imports; falls back gracefully when Azure is not configured.
- [app/core/config.py](app/core/config.py) — Added `USE_AZURE_STOContextE` flag (default `false`) and local path settings (`LOCAL_STOContextE_BASE_PATH`, `LOCAL_STOContextE_Context_DOCS_PATH`, etc.).

**Local storage layout:**
```
./data/uploads/
  context_docs/          # uploaded Context source documents
  published/         # exported HTML stories
  generated_images/  # AI-generated images
  blog_media/        # blog image uploads
```

**Routers not yet migrated:** `app/routers/story.py` contains one publish-to-blob endpoint that still instantiates `BlobServiceClient` directly and is Azure-only. This endpoint raises a 500 if Azure is not configured, which is acceptable until a local publish path is added.

---

### 5. Lazy Azure SDK Imports

**Problem:** Even with Azure disabled, several files imported `from azure.storage.blob.aio import BlobServiceClient` at module level. Because all routers are loaded at startup, this meant the Azure SDK had to be importable (though not necessarily connected to any cloud service).

**Approach:** The Azure SDK packages are kept in `requirements.txt` (they are free to install; cost only accrues when you use the services). The key change was ensuring no Azure imports happen unless actually needed at runtime. Services that previously held Azure clients as module-level globals now use lazy imports inside functions.

**Files changed:**
- `app/services/semantic_kernel_setup.py` — Azure SK connector only imported when `ACTIVE_LLM_PROVIDER == "AZURE"`
- `app/services/embedding_service.py` — Azure OpenAI client fully removed
- `app/services/context_retrieval.py` — Azure Search SDK fully removed
- `app/core/azure_deps.py` — Azure imports inside `if settings.USE_AZURE_STOContextE` branch
- `app/services/azure_blob_service.py` — Azure imports inside methods

**Still hard-importing:** Several router files (`character.py`, `location.py`, `lore_item.py`, `act.py`, `scene.py`, `world.py`, etc.) still have `from azure.storage.blob.aio import BlobServiceClient` at the top, but only as type annotations for `Depends()` parameters. These do not cause startup failures because the SDK is installed; they are cosmetically still Azure-coupled but functionally route through `LocalStorageClient` at runtime.

---

### 6. Configuration Restructure

The entire `app/core/config.py` `Settings` class was reorganised to reflect the new provider hierarchy:

**Before:** Azure OpenAI was at the top; OpenRouter was an afterthought near the bottom.

**After:**
1. OpenRouter settings (primary, with sensible defaults)
2. Standard OpenAI settings (alternative)
3. Local embedding settings
4. ChromaDB vector DB settings
5. Local file storage settings
6. Azure OpenAI (legacy/optional, clearly labelled)
7. Azure Blob Storage (controlled by `USE_AZURE_STOContextE` flag)
8. Azure AI Search (controlled by `USE_AZURE_SEARCH` flag)

The `.env_template` was rewritten to match — it now works out-of-the-box for a developer who only has an OpenRouter API key.

---

### 7. React SPA Groundwork — Token Authentication

**Approach:** The existing cookie-based authentication was extended to also support `Authorization: Bearer <token>` headers. Both methods work simultaneously, enabling React to use tokens while the Jinja2 frontend continues using cookies.

**Files changed:**
- [app/core/deps.py](app/core/deps.py) — `get_current_user()` now checks the `Authorization` header first, falls back to the `access_token` cookie
- [app/routers/auth.py](app/routers/auth.py) — Added three new endpoints:
  - `POST /api/v1/auth/token` — OAuth2-compatible, returns `access_token` + `refresh_token`
  - `POST /api/v1/auth/refresh` — Validates and rotates refresh tokens
  - `POST /api/v1/auth/logout` — Clears cookie and optionally revokes all refresh tokens

**Zero breaking changes:** Existing Jinja2 frontend is unaffected.

---

### 8. API Response Standardisation (Partial)

**Approach:** A base `ApiResponse` wrapper schema was created to give React a consistent response envelope.

**Files changed:**
- [app/schemas/base.py](app/schemas/base.py) — New file. Defines `ApiResponse`, `ApiMeta`, `ApiError`, `PaginationMeta`
- [app/routers/world.py](app/routers/world.py) — All 9 endpoints fully wrapped with `ApiResponse.success_response()`
- [app/routers/story.py](app/routers/story.py) — Partially wrapped (4 of 8 endpoints)

**Status:** 2 of ~50 routers are fully wrapped. The remaining routers have `response_model=ApiResponse` declared but still return raw objects. This is non-breaking (FastAPI serialises to the declared model shape) but inconsistent. A wrapping pass is needed for full React compatibility.

---

## What Was NOT Changed

- **Database:** PostgreSQL + SQLAlchemy async — unchanged
- **Auth mechanism:** JWT with Argon2 password hashing — unchanged
- **Semantic Kernel:** Still used for LLM orchestration; only the service connectors changed
- **Router logic:** All business logic in routers is unchanged
- **Frontend templates:** Jinja2 templates continue to work as before
- **WebSocket connections:** Act/scene AI writing via WebSocket — unchanged

---

## New Dependencies

| Package | Purpose | Default |
|---|---|---|
| `sentence-transformers==3.4.1` | Local embeddings | Always active |
| `torch>=2.0.0` | Required by sentence-transformers | Always active |
| `chromadb==0.6.3` | Local vector database | Always active |

## Dependencies Made Optional (Still in requirements.txt)

| Package | Now Used When |
|---|---|
| `azure-identity==1.23.0` | `USE_AZURE_STOContextE=true` or `ACTIVE_LLM_PROVIDER=AZURE` |
| `azure-storage-blob[aio]==12.25.1` | `USE_AZURE_STOContextE=true` |
| `azure-search-documents==11.5.2` | `USE_AZURE_SEARCH=true` |

These are kept in `requirements.txt` because several router files still import the type at module level. The SDKs are free to install and incur no cost unless you configure credentials and call the services.

---

## Running Without Azure

1. Copy `.env_template` to `.env`
2. Set `OPENROUTER_API_KEY` to your OpenRouter key (free tier available)
3. Leave all `USE_AZURE_*` flags as `false`
4. Run `alembic upgrade head` then `uvicorn app.main:app --reload`

The app will:
- Use OpenRouter for all LLM calls
- Download `all-MiniLM-L6-v2` on first startup for embeddings (~90 MB)
- Store vector data in `./data/chromadb`
- Store uploaded files in `./data/uploads`

---

## Running With Azure (Optional Upgrade)

Set the following in `.env` to re-enable specific Azure services:

```bash
USE_AZURE_STOContextE=true
AZURE_STOContextE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...

USE_AZURE_SEARCH=true          # not yet implemented in new service layer
AZURE_AI_SEARCH_SERVICE_ENDPOINT=https://YOUR_SERVICE.search.windows.net
AZURE_AI_SEARCH_API_KEY=...

ACTIVE_LLM_PROVIDER=AZURE
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=...
```

---

## Known Gaps / Future Work

1. **Story publish endpoint** (`/api/v1/stories/{id}/publish`) — still Azure Blob only; needs a local-filesystem publish path
2. **API response wrapping** — ~48 routers still return raw objects instead of `ApiResponse`-wrapped data
3. **`azure_ai_search_service.py`** — legacy service file no longer imported by any app code; can be deleted once Azure Search is confirmed no longer needed
4. **Re-ingestion required** — existing content indexed in Azure AI Search (1536-dim) cannot be directly migrated to ChromaDB (384-dim default); documents must be re-uploaded and re-indexed
5. **CRUD count methods** — pagination totals use `len(results)` as a workaround; proper `COUNT` queries needed for large datasets

