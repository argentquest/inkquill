# Ink And Quill

Ink And Quill is a full-stack AI storytelling platform built around a FastAPI backend and an in-progress React frontend rebuild. It helps users create and manage worlds, stories, scenes, prompts, and related creative content while using AI-assisted workflows for drafting, refinement, and context-aware generation.

## Overview

The platform combines structured story authoring with world-building tools such as characters, locations, and lore items. Those assets, along with uploaded documents, can be used as context for AI-assisted writing and chat flows.

The repository is currently backend-first in its delivery approach. The active frontend rebuild lives in `frontendv1/`, while the backend continues to provide the stable API surface and supporting business logic that the React client will consume.

## Core Capabilities

- User authentication and session management
- Story, act, and scene authoring flows
- World-building with characters, locations, and lore items
- Prompt management and AI-assisted writing workflows
- Document upload and context ingestion pipelines
- Background job processing and status tracking
- Billing, admin, blog, forum, and community-oriented routes
- Story publishing and related content delivery features

## Technology Stack

- Backend: Python, FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL
- AI integrations: Azure OpenAI, LangChain, LangGraph
- Search and storage: Azure AI Search, Azure Blob Storage
- Frontend rebuild: Next.js 15, React 19, Tailwind CSS, React Query, React Hook Form, Zod
- Testing: Pytest for backend, Playwright for frontend browser verification
- Deployment: Docker and environment-based configuration

## Repository Structure

```text
app/           FastAPI application code: routers, services, models, schemas, CRUD, templates, static assets
alembic/       Database migration configuration
migrations/    Migration assets used by the project
frontendv1/    Active React frontend rebuild workspace
tests/         Unit and integration test suites
docs/          Supporting documentation
plans/         Planning and implementation notes
```

## Local Development

### Backend

1. Create and activate the virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env_template` to `.env` and fill in the required settings.
4. Run migrations with `alembic upgrade head`.
5. Start the app with `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

The backend is typically available at `http://localhost:8000`, with Swagger docs at `http://localhost:8000/docs`.

### Frontend

The active frontend workspace is `frontendv1/`.

1. Install dependencies in `frontendv1/`.
2. Run the development server with `npm run dev`.
3. Build the frontend with `npm run build`.

## Testing

Common project test commands are documented in `AGENTS.md`. The standard workflows include:

- Backend unit tests
- Backend unit plus integration tests
- Backend coverage checks
- Frontend production build
- Frontend Playwright end-to-end tests

## Notes

- `README.md` has been aligned with the current repository direction and cleaned of merge-conflict markers.
- Planning docs such as `frontendAll.md`, `reacttools.md`, and the sprint markdown files describe the React rebuild in more detail.
