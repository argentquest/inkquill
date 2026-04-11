# Requirements.txt — Unused Dependencies Analysis

**Date:** 2026-04-11  
**Scope:** All packages listed in `requirements.txt` cross-referenced against active `app/` codebase.

---

## Summary

| Status | Count |
|--------|-------|
| Actively Used | 22 |
| Conditionally Used (optional/fallback) | 4 |
| Not Used / Dead Dependencies | 5 |

---

## Dependencies NOT In Use (Remove Candidates)

These packages are listed in `requirements.txt` but have **no active imports or usage** anywhere in the `app/` codebase.

| Package | Version | Notes |
|---------|---------|-------|
| **`semantic-kernel`** | `1.33.0` | No `import semantic_kernel` or `from semantic_kernel` exists in active code. All references are in `archive/` (legacy scripts), comments, or feature-detection checks (`importlib.util.find_spec`). The codebase has migrated to LangGraph. |
| **`sentence-transformers`** | `3.4.1` | Zero imports in `app/`. No `SentenceTransformer` usage anywhere. |
| **`torch`** | `>=2.0.0` | Zero imports in `app/`. Only relevant as a dependency of `sentence-transformers`, which is itself unused. |
| **`chromadb`** | `0.6.3` | Zero imports in `app/`. No vector database usage. |
| **`itsdangerous`** | `2.2.0` | Zero direct imports. `authlib` may use it internally, but the project does not import it directly. If `authlib` needs it, it should be a transitive dependency, not a direct one. |

### Recommended Action
Remove these 5 packages from `requirements.txt`. They add install weight and potential security surface without providing value.

---

## Conditionally Used Dependencies (Keep, But Note)

These packages are used in optional/fallback paths or only in specific contexts.

| Package | Version | Usage Context |
|---------|---------|---------------|
| **`python-docx`** | `1.1.2` | Used in [`app/processing/text_extraction.py`](app/processing/text_extraction.py:19) inside a try/except fallback. DOCX processing is gracefully degraded if missing. |
| **`PyMuPDF`** | `1.26.1` | Used in [`app/processing/text_extraction.py`](app/processing/text_extraction.py:12) inside a try/except fallback. PDF processing is gracefully degraded if missing. |
| **`gunicorn`** | `23.0.0` | Only used in [`Dockerfile`](Dockerfile:48) and deployment scripts. Not imported in Python code. Required for production deployment but not for development/testing. |
| **`pytest-asyncio`** | `1.0.0` | Used in test files (e.g., [`tests/unit/care_circle/test_care_circle_providers.py`](tests/unit/care_circle/test_care_circle_providers.py:2)). Required for async test support. |

---

## Actively Used Dependencies (Keep)

These packages are actively imported and used in the `app/` codebase.

### Core Web Framework
| Package | Usage |
|---------|-------|
| **`fastapi`** | Extensively used across all routers, middleware, and core modules |
| **`uvicorn`** | Used in [`app/main.py`](app/main.py:40) for ProxyHeadersMiddleware |

### Database & ORM
| Package | Usage |
|---------|-------|
| **`sqlalchemy`** | Used in all models, CRUD operations, and database configuration |
| **`asyncpg`** | Used in [`app/scripts/security_scan.py`](app/scripts/security_scan.py:8) and test conftest |
| **`alembic`** | Used via CLI for migrations; referenced in `alembic.ini` |

### Data Validation & Settings
| Package | Usage |
|---------|-------|
| **`pydantic-settings`** | Used in [`app/core/config.py`](app/core/config.py:7) for BaseSettings |
| **`pydantic`** | Used extensively in all schemas and request/response models |

### Authentication & Security
| Package | Usage |
|---------|-------|
| **`python-jose`** | Used in [`app/core/security.py`](app/core/security.py:7) for JWT encoding/decoding |
| **`passlib`** | Used in [`app/core/security.py`](app/core/security.py:8) and [`app/services/oauth_service.py`](app/services/oauth_service.py:11) for password hashing |

### OAuth & Social Authentication
| Package | Usage |
|---------|-------|
| **`authlib`** | Used in [`app/core/oauth_config.py`](app/core/oauth_config.py:5) for OAuth client setup |
| **`httpx`** | Used extensively in care circle providers and [`app/routers/social_preview.py`](app/routers/social_preview.py:17) |

### AI & LangGraph
| Package | Usage |
|---------|-------|
| **`openai`** | Used in scene processor, AI writing, image generation, and cost tracking |
| **`langchain`** | `langchain_core` imported in [`app/services/langgraph_kernel.py`](app/services/langgraph_kernel.py:14) |
| **`langgraph`** | Used in [`app/services/langgraph_kernel.py`](app/services/langgraph_kernel.py:15) for StateGraph |
| **`langchain-openai`** | Used in [`app/services/langgraph_kernel.py`](app/services/langgraph_kernel.py:16) for ChatOpenAI |
| **`tiktoken`** | Used in [`app/services/cost_tracker_service.py`](app/services/cost_tracker_service.py:8) for token counting |

### File Storage & Processing
| Package | Usage |
|---------|-------|
| **`aiofiles`** | Used in [`app/services/storage/local_storage.py`](app/services/storage/local_storage.py:6) for async file I/O |
| **`python-multipart`** | Used implicitly by FastAPI for `UploadFile`/`Form` handling (FastAPI requires it) |
| **`markdownify`** | Used in scene processor, AI writing routers, and WS context manager |
| **`reportlab`** | Used in [`app/services/pdf_export_service.py`](app/services/pdf_export_service.py:13) for PDF generation |
| **`pillow`** | Used in blog media, image generation, and social preview routers |
| **`markdown`** | Used in [`app/services/story_brainstorm_service.py`](app/services/story_brainstorm_service.py:10) |

### Puzzle & Game Generation
| Package | Usage |
|---------|-------|
| **`python-constraint`** | Used in [`app/services/care_circle/providers/crossword/provider.py`](app/services/care_circle/providers/crossword/provider.py:29) for CSP solving |
| **`word-search-generator`** | Used in [`app/services/care_circle/providers/puzzle/provider.py`](app/services/care_circle/providers/puzzle/provider.py:2) for word search puzzles |

### Testing
| Package | Usage |
|---------|-------|
| **`pytest`** | Used in 54+ test files |

---

## Recommended Changes to `requirements.txt`

### Remove these lines:
```
semantic-kernel==1.33.0
sentence-transformers==3.4.1
torch>=2.0.0
chromadb==0.6.3
itsdangerous==2.2.0
```

### Resulting cleaned `requirements.txt`:
```
# --- Core Web Framework ---
fastapi==0.115.12
uvicorn[standard]==0.34.3

# --- Database & ORM ---
sqlalchemy==2.0.41
asyncpg==0.30.0
alembic==1.16.1

# --- Data Validation & Settings ---
pydantic-settings==2.9.1
pydantic[email]==2.11.5

# --- Authentication & Security ---
python-jose[cryptography]==3.5.0
passlib[argon2]==1.7.4

# --- OAuth & Social Authentication ---
authlib==1.3.2
httpx==0.28.1

# --- AI & LangGraph ---
openai==1.86.0
langchain==0.3.25
langgraph==0.2.60
langchain-openai==0.2.14
tiktoken==0.9.0

# --- Local/Cloud-agnostic File Storage ---
aiofiles==24.1.0

# --- Document Processing & Content Conversion ---
PyMuPDF==1.26.1
python-docx==1.1.2
markdownify==1.1.0
reportlab==4.0.4

# --- File Uploads for FastAPI ---
python-multipart==0.0.20

# --- Testing Framework ---
pytest==8.4.0
pytest-asyncio==1.0.0

# --- Optional: Process Management (for Production) ---
gunicorn==23.0.0

# --- Image Processing ---
pillow
markdown

python-constraint==1.4.0
word-search-generator==5.0.0
```

---

## Notes

1. **`semantic-kernel`**: The codebase has a feature-detection pattern (`orchestration_backend_is_semantic_kernel()`) but the actual `semantic_kernel` package is never imported in active code. All semantic kernel references in `app/services/__init__.py` are commented out. The LangGraph kernel (`app/services/langgraph_kernel.py`) is the active AI orchestration backend.

2. **`sentence-transformers`**, **`torch`**, **`chromadb`**: These were likely intended for local embedding/vector search functionality that was never implemented or was replaced by cloud-based alternatives (OpenAI embeddings via the API).

3. **`itsdangerous`**: This is a transitive dependency of `authlib` and `python-jose`. No need to declare it explicitly.

4. **`gunicorn`**: Only used in production deployment (Dockerfile, Azure App Service). Consider moving to a `requirements-prod.txt` or keeping with a comment noting it's deployment-only.

5. **`PyMuPDF`** and **`python-docx`**: Both are used with graceful degradation (try/except). They are optional at runtime but recommended for full document processing functionality.
