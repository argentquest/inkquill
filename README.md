# AI Storytelling Assistant with Worlds & Context

## 1. Overview

The AI Storytelling Assistant is a web application built with FastAPI, designed to help users craft and develop structured stories. It leverages Large Language Models (LLMs) via Azure OpenAI Service for content generation and refinement.

A key feature is the integrated World-Building toolkit, allowing users to define detailed **Worlds** with unique **Characters**, **Locations**, and **Lore Items**. These world elements, along with user-uploaded documents, form a rich knowledge base for **direct context assembly**, enabling the AI to provide deeply context-aware and factually grounded assistance.

The application features secure user authentication, comprehensive project management, asynchronous job processing with real-time status feedback, and a powerful "Import World from Book Title" feature.

## 2. Core Features

*   **User Authentication:** Secure registration and login using JWTs stored in HttpOnly cookies.
*   **World-Building Toolkit:**
    *   **Worlds:** Create, read, update, and delete unique fictional Worlds that serve as containers for all your lore.
    *   **Characters, Locations, & Lore Items:** Define detailed world elements with descriptions, traits, and other metadata.
    *   **AI-Powered World Import:** Generate a foundational world structure (characters, locations, lore) by simply providing the title of a classic book.
*   **Project Management:**
    *   **Stories:** Create and manage distinct story projects, each of which **must** be associated with a World.
    *   **Acts & Scenes:** Structure your narratives logically using acts and scenes with rich text editing capabilities.
    *   **World Element Linking:** Explicitly link characters, locations, and lore from your World to a specific Story to provide the AI with highly relevant context.
*   **Prompt Library:** A personal and shared library for creating, managing, and reusing prompts to instruct the AI effectively.
*   **Context System & Asynchronous Job Processing:**
    *   **World Element Context:** When a world element is created or updated, a background job automatically generates a descriptive text summary, embeds it, and indexes it into Azure AI Search, making your lore instantly available to the AI.
    *   **User Document Uploads:** Upload your own documents (PDF, DOCX, TXT) and associate them with a World to expand the AI's knowledge base.
    *   **Job Status Tracking:** All long-running background tasks (like document ingestion or world imports) are tracked, providing real-time status updates to the user.
*   **AI-Assisted Content Generation:**
    *   **Interactive Editors:** Dedicated editors for Acts and Scenes with real-time AI assistance via WebSockets.
    *   **Context-Aware AI:** The Context system automatically retrieves relevant information from your world elements and documents to inform the AI's creative process.
    *   **Cost & Latency Tracking:** Every call to an AI service is logged to a database table, recording token usage, calculated cost, and round-trip time for monitoring and analysis.
*   **Publishing:** Compile a finished story into a single, shareable HTML file.

## 3. Technology Stack

*   **Backend:** Python 3.12+, FastAPI, Uvicorn, Gunicorn
*   **AI Orchestration:** LangChain + LangGraph
*   **AI Models:** Azure OpenAI Service (Chat Completion & Text Embedding)
*   **Database:** PostgreSQL (driver: `asyncpg`)
*   **ORM & Migrations:** SQLAlchemy (asyncio), Alembic
*   **Vector Search / Context Store:** Azure AI Search
*   **Storage:** Azure Blob Storage
*   **Authentication:** JWT (via `python-jose`), Password Hashing (`passlib[bcrypt]`)
*   **Frontend:** Jinja2 Templating, Vanilla JavaScript (Fetch, WebSockets), Bootstrap 5, Quill.js
*   **Validation & Settings:** Pydantic
*   **Key SDKs:** `openai`, `azure-identity`, `azure-storage-blob`, `azure-search-documents`
*   **Content Processing:** `tiktoken`, `PyMuPDF`, `python-docx`, `markdownify`

## 4. Project Structure

`/story_app/`
|
|-- `/app/`
|   |-- `/core/`                # Config, security, logging, shared dependencies & utilities
|   |-- `/db/`                  # SQLAlchemy setup
|   |-- `/models/`              # SQLAlchemy ORM models (user.py, world.py, job_status.py, etc.)
|   |-- `/schemas/`             # Pydantic schemas (user.py, world.py, job_status.py, etc.)
|   |-- `/crud/`                # Database CRUD operations
|   |-- `/routers/`             # API & UI endpoint definitions
|   |-- `/services/`            # Business logic (LangGraph/LangChain orchestration, context, cost tracking, etc.)
|   |-- `/processing/`          # Background task logic (Context ingestion, world import)
|   |-- `/prompts/`
|   |-- `/static/`
|   |-- `/templates/`
|   |-- `main.py`               # FastAPI application entry point
|
|-- `/alembic/`                 # Database migrations
|-- `/logs/`                    # Log files (gitignored)
|-- `.env`                      # Local environment variables (GITIGNORED)
|-- `Dockerfile` & `docker-compose.yml`
|-- `requirements.txt`
|-- `README.md`                 # This file

## 5. Local Development Setup

#### Prerequisites
*   Python 3.11+
*   PostgreSQL Server (can be run via Docker)
*   Azure Subscription with access to: Azure OpenAI, Azure AI Search, and Azure Blob Storage.

#### Step-by-Step Guide
1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd story_app
    ```

2.  **Set up Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # .\.venv\Scripts\activate    # On Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Copy the `.env_template` file to a new file named `.env`.
    *   Open `.env` and fill in all required values for your PostgreSQL database and Azure services (endpoints, keys, deployment names).
    *   The `AUTH_SECRET_KEY` should be a long, random string.
    *   You can adjust `LOG_LEVEL_CONSOLE` (e.g., to `DEBUG`) for more detailed output during development.

5.  **Set Up the Database:**
    *   Ensure your PostgreSQL server is running.
    *   Create the database with the name you specified in your `.env` file (e.g., `devstory2`).
    *   Run the Alembic migrations to create all necessary tables:
        ```bash
        alembic upgrade head
        ```

## 6. Running the Application

1.  **Activate your virtual environment.**
2.  **Start the FastAPI Server** from the project root directory:
    ```bash
    .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    Using the project interpreter matters on Windows. If you start `uvicorn` from a global Python install instead of `.venv`, imports like `sqlalchemy` can fail even when they are present in `requirements.txt`.
3.  **Monitor the Startup Logs:** Watch the terminal for logs from `app.main` and `app.core.config`. They will confirm that your settings have been loaded correctly.
4.  **Access the Application:**
    *   **UI:** Open your browser to `http://localhost:8000/`.
    *   **API Docs (Swagger):** `http://localhost:8000/docs`.

## 7. Testing

*   **Diagnostic Scripts:** The `app/` directory contains several `maintest_*.py` and `test_*.py` scripts useful for standalone checks of infrastructure components (database, storage, AI services). These are run manually and are separate from the formal test suite.
*   **Formal Test Suite:** The `tests/` directory contains a `pytest`-based suite. To run it:
    ```bash
    pytest
    ```
    *(Note: This suite may require separate test database configuration as defined in `tests/conftest.py`).*
