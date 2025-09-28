# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application

**Development:**
```bash
# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# .\.venv\Scripts\activate    # On Windows

# Run with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Use Docker Compose for full stack
docker-compose up
```

**Production:**
```bash
# Uses Gunicorn with Uvicorn workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Database Management

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1
```

### Testing

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_filename.py::test_function_name

# Test infrastructure connections (manual diagnostic scripts)
python app/test_ai_search_service.py
python app/test_infra_check.py
```

### Linting & Type Checking

The project uses standard Python tooling. Common commands:
```bash
# Install dev dependencies if needed
pip install flake8 mypy black

# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

## High-Level Architecture

### Core Architecture

This is a **FastAPI-based AI Storytelling Assistant** with integrated world-building and RAG capabilities. The application follows a layered architecture:

1. **API Layer** (`app/routers/`): REST endpoints and WebSocket connections
2. **Business Logic** (`app/services/`): AI orchestration, RAG retrieval, cost tracking
3. **Data Layer** (`app/crud/`, `app/models/`): Database operations via SQLAlchemy async
4. **AI Integration**: Microsoft Semantic Kernel for LLM orchestration

### Key Architectural Components

#### WebSocket-Based Real-Time AI Assistance
- **Act Editor** (`ai_assisted_writing.py`): Real-time AI assistance for writing acts
- **Scene Editor** (`ai_scene_writing.py`): Real-time AI assistance for writing scenes
- Uses WebSocket connections with ticket-based authentication
- Implements connection managers for handling multiple concurrent sessions

#### RAG (Retrieval Augmented Generation) System
- **Azure AI Search** integration for vector search
- **Embedding Service** (`embedding_service.py`): Generates embeddings using Azure OpenAI
- **Background Jobs** (`app/processing/`): Asynchronous processing for:
  - Document ingestion and chunking
  - World element indexing
  - RAG text generation from structured data

#### Semantic Kernel Integration
- **Central Configuration** (`semantic_kernel_setup.py`): Loads prompts, configures AI services
- **Prompt Management**: System prompts stored in `app/prompts/system/`
- **Plugin Architecture**:
  - `StorytellingPlugin`: Narrative generation
  - `StoryAnalysisPlugin`: Content analysis and metadata extraction
  - `WorldBuildingPlugin`: RAG text conversion for world elements
  - `RetrievalPlugin`: RAG context retrieval

#### AI Model Management
- **Dynamic Model Configuration** (`ai_model_config.py`): Database-stored AI model settings
- **Model Cache** (`ai_model_cache.py`): In-memory cache for model configurations
- **Cost Tracking** (`cost_tracker_service.py`): Logs all AI API calls with token usage and costs

#### Authentication & Security
- JWT-based authentication with HttpOnly cookies
- WebSocket authentication via temporary tickets
- Password hashing with Argon2

### Data Flow for AI-Assisted Writing

1. **User Action**: User types in the web editor
2. **WebSocket Message**: Frontend sends content + metadata to backend
3. **RAG Retrieval**: System queries Azure AI Search for relevant context
4. **AI Generation**: Semantic Kernel invokes appropriate function with context
5. **Response Stream**: AI response streamed back via WebSocket
6. **Cost Logging**: Token usage and costs logged to database

### World-Building & RAG Pipeline

1. **Element Creation**: User creates character/location/lore item
2. **Background Job**: System queues RAG text generation task
3. **Text Generation**: AI converts structured data to descriptive text
4. **Embedding**: Text embedded using Azure OpenAI
5. **Indexing**: Embedded text indexed in Azure AI Search
6. **Retrieval**: Available for future AI-assisted writing sessions

### Key Configuration Points

- **Environment Variables**: All Azure service endpoints, keys, and deployment names in `.env`
- **AI Settings**: Temperature, max tokens, and top_p configured per operation type in `config.py`
- **Logging**: Comprehensive logging with configurable levels (console/file)
- **CORS**: Configured for local development, adjustable for production

### Database Schema

Uses PostgreSQL with async support. Key tables:
- `users`: Authentication and user management
- `worlds`: Container for all world-building elements
- `stories`: Projects associated with worlds
- `acts`/`scenes`: Story structure
- `characters`/`locations`/`lore_items`: World elements
- `ai_model_configs`: Dynamic AI model settings
- `ai_cost_logs`: Token usage and cost tracking
- `job_statuses`: Background job tracking

## UI Design Standards & Rules

**CRITICAL: All UI development must follow these Tabler Premium design standards.**

### 1. Container Layout Rules
- **Full Width**: Always use `container-fluid` instead of `container-xl` for all pages
- **Responsive**: All layouts must work on mobile, tablet, and desktop
- **Consistent Spacing**: Use Tabler CSS variables for margins and padding (`var(--tblr-gutter-x)`)

### 2. Header Standards (MANDATORY - EVERY PAGE MUST HAVE A HERO HEADER)
- **REQUIRED ON EVERY PAGE**: All pages MUST have gradient hero headers - NO EXCEPTIONS
- **Enhanced Hero Headers**: Gradient backgrounds with consistent styling across the entire application
- **Gradient Background**: `linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%)`
- **Background Pattern**: Add radial gradient overlays for visual depth
- **Margin Reduction**: Top margin reduced by 75% (`calc(var(--tblr-gutter-x, 1.5rem) * 0.7)`)
- **Text Contrast**: White text with proper contrast against gradient backgrounds
- **Action Buttons**: Primary actions placed in header area, not below
- **Header Structure**: Title, subtitle, stats badge, and action buttons in header
- **Standard Hero Template**: Use the established pattern from other pages for consistency

### 3. Button Standards (STRICT)
- **Help Buttons**: Always use `btn btn-warning` for consistent yellow/orange styling
- **Action Buttons**: Use `btn btn-primary` for consistency within card groups
- **Header Buttons**: Use `btn btn-light` against gradient backgrounds
- **Text Labels**: All buttons MUST have descriptive text, not just icons
- **Icon Spacing**: Always use `me-1` class between icons and text
- **Tooltips**: All buttons must have descriptive tooltips

### 4. Card Component Standards
- **Tabler Card Structure**: Use proper card headers, bodies, and footers
- **Hover Effects**: 
  - `translateY(-4px)` on hover
  - Enhanced box shadows (`var(--tblr-box-shadow-lg)`)
  - Border color changes to primary
- **Animated Borders**: Gradient top borders that slide in on hover using CSS transforms
- **Status Indicators**: Use status badges with gradient backgrounds
- **Metadata Sections**: Consistent styling with `var(--tblr-bg-surface-secondary)`

### 5. Animation Standards
- **Fade-in Animations**: `fadeInUp` with staggered delays for multiple items (0.1s increments)
- **Smooth Transitions**: `cubic-bezier(0.4, 0, 0.2, 1)` for premium feel
- **Hover Transitions**: All interactive elements have 0.2-0.3s transitions
- **Loading States**: Tabler progress bars with indeterminate animation

### 6. Color & Theme Standards (CRITICAL)
- **CSS Variables**: Always use Tabler CSS variables (`var(--tblr-primary)`, `var(--tblr-purple)`)
- **Consistent Gradients**: Primary to purple gradients throughout application
- **Text Contrast**: 
  - Light backgrounds: `text-dark`
  - Dark/gradient backgrounds: `text-white`
- **Badge Contrast**: `bg-light text-dark` on gradient backgrounds for readability

### 7. Form & Input Standards
- **Tabler Form Controls**: Enhanced styling with focus states
- **Floating Labels**: Support for Tabler floating label pattern when appropriate
- **Input Transitions**: Smooth focus transitions with primary color
- **Error States**: Consistent error styling across all forms

### 8. Modal Standards
- **Enhanced Headers**: Gradient backgrounds with center-aligned titles
- **Proper Sizing**: `modal-xl` with responsive viewport sizing
- **Button Actions**: Consistent button styling within modals
- **Loading States**: Tabler card-based loading indicators

### 9. Empty State Standards
- **Large Avatars**: Use `avatar-xl` with appropriate icons
- **Helpful Copy**: Descriptive text explaining next steps
- **Primary Actions**: Clear call-to-action buttons
- **Status Bars**: `card-status-top` for visual hierarchy

### 10. Typography Standards
- **Page Titles**: Consistent sizing with appropriate FontAwesome icons
- **Subtitles**: Descriptive text using `text-secondary`
- **Small Text**: Use `small` class for metadata and timestamps
- **Icon Consistency**: FontAwesome icons with consistent sizing throughout

### 11. Spacing & Layout Rules
- **Header Spacing**: 
  - Reduced top margins by 75%
  - Consistent bottom spacing (`margin-bottom: 2rem`)
- **Card Spacing**: Use `row-cards` for consistent card grids
- **Button Lists**: Use `btn-list` for grouped buttons with `flex-wrap`
- **Flex Utilities**: Use `flex-wrap` for responsive button layouts

### 12. Interactive Element Standards
- **Tooltips**: All interactive elements must have helpful tooltips
- **Loading Feedback**: Show loading states for all async operations
- **Error Handling**: Graceful error states with retry options
- **Accessibility**: Proper ARIA labels and keyboard navigation

### 13. Premium Feature Usage (REQUIRED)
- **Status Bars**: Use card status bars for visual hierarchy
- **Ribbons**: Add ribbons for special statuses when appropriate
- **Enhanced Shadows**: Use Tabler's enhanced shadow system
- **Pattern Overlays**: Subtle background patterns for depth

### 14. Navigation Standards
- **Sidebar Layout**: Consistent sidebar navigation
- **Breadcrumbs**: Clear navigation hierarchy where appropriate
- **Active States**: Proper highlighting of current page/section

### 15. Image & Media Standards
- **Square Containers**: Consistent 1:1 aspect ratio for card images
- **Placeholder States**: Attractive placeholders when no image available
- **Responsive Images**: Proper `object-fit: cover` for image scaling

### Implementation Requirements
- **Always** check existing pages for pattern consistency before implementing new UI
- **Never** use basic Bootstrap components when Tabler Premium alternatives exist
- **Always** use Tabler CSS variables instead of hardcoded colors
- **Never** create inconsistent button styling - follow the established patterns
- **Always** implement hover effects and animations for interactive elements
- **Never** forget to add descriptive text to buttons (not just icons)