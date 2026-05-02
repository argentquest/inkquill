# Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ (for the React frontend)
- Docker + Docker Compose (recommended for local dev)
- PostgreSQL (if running without Docker)

---

## Quick Start (Docker — recommended)

This is the easiest path. Docker handles the database, backend, and frontend together with hot reload.

**1. Copy and configure environment**

```powershell
cp .env_template .env
```

Open `.env` and fill in at minimum:

- `AUTH_SECRET_KEY` — generate one with:
  ```powershell
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- `OPENROUTER_API_KEY` — get a free key at https://openrouter.ai

Everything else has sensible defaults for local dev.

**2. Start the dev stack**

```powershell
docker compose -p inkandquill-dev -f docker-compose.yml -f infra/docker-compose.dev.yml up --build -d
```

**3. Run database migrations**

```powershell
docker compose -p inkandquill-dev -f docker-compose.yml -f infra/docker-compose.dev.yml run --rm backend alembic upgrade head
```

**4. Open the app**

| URL | What |
|-----|------|
| `http://localhost:8080` | Main app (gateway) |
| `http://localhost:18000/docs` | FastAPI Swagger UI |

**Stop the stack:**

```powershell
docker compose -p inkandquill-dev -f docker-compose.yml -f infra/docker-compose.dev.yml down
```

---

## Manual Setup (no Docker)

Use this if you want to run Python and Node directly on your machine.

### Backend

**1. Create a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment**

```powershell
cp .env_template .env
# Edit .env — set AUTH_SECRET_KEY, database connection, and LLM key
```

**3. Run migrations**

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

**4. Start the backend**

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Backend is available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Frontend

```powershell
cd frontendv1
npm install
npm run dev
```

Frontend runs at `http://localhost:3001` (proxies API requests to the backend).

---

## Running Tests

Unit tests only:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit -q
```

Unit + integration (stable subset):

```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit tests\integration --ignore=tests/integration/shared/test_document_upload_integration.py --ignore=tests/integration/shared/test_image_generation_integration.py -q
```

Frontend Playwright tests:

```powershell
cd frontendv1
npm run test:e2e
```

---

## Environment Variables Reference

See [.env_template](.env_template) for the full list with descriptions. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `AUTH_SECRET_KEY` | Yes | JWT signing secret |
| `OPENROUTER_API_KEY` | Yes | LLM API key (free tier available) |
| `POSTGRES_*` | Yes | Database connection settings |
| `OPENAI_API_KEY` | Only for image gen | Required if `ACTIVE_IMAGE_PROVIDER=DALLE3` |
| `GOOGLE_OAUTH_CLIENT_ID/SECRET` | No | Enable Google login |
| `SMTP_*` | No | Enable email features |

---

## Other Environments

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for stage, test, prod, and Azure App Service deployment.
