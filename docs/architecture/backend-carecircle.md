# Backend CareCircle Architecture Document

## 1. Overview

The CareCircle backend provides APIs and services for managing family care circles, patient profiles, content providers, and daily patient sessions. It supports two distinct user flows:
- **Family Management**: Authenticated users manage patients, configure providers, and monitor care delivery.
- **Patient Access**: Patients authenticate via image-based selection and receive daily curated content cards.

### Key Characteristics
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (async via SQLAlchemy)
- **ORM**: SQLAlchemy 2.0 (async)
- **Architecture**: Router → CRUD → Model layers
- **Testing**: pytest (unit + integration)

### Accuracy Review
- **Last reviewed**: 2026-04-05
- Reviewed against:
  - `app/routers/care_circle.py` (9 endpoints, all implemented)
  - `app/crud/care_circle.py` (CRUD functions, 32-provider catalog seed, 2 default patients)
  - `app/services/care_circle/provider_base.py` (base interface with execute/execute safety wrapper)
  - `app/services/care_circle/session_assembler.py` (sequential execution, on-demand regeneration)
  - `app/models/care_circle.py` (8 SQLAlchemy models)
  - `app/schemas/care_circle.py` (Pydantic schemas for request/response validation)
- **Implementation status**:
  - **Fully implemented**: All 9 documented API endpoints are wired and functional.
  - **On-demand session assembly**: `GET /api/v1/care-circle/patient/session/{patient_id}` triggers `assemble_daily_patient_session()` synchronously before reading the session payload back. This is intentional for Sprint 2 stabilization.
  - **Sequential provider execution**: Session assembly runs providers sequentially (not concurrently). The code comment mentions `asyncio.gather` for production but sequential is the current behavior.
  - **Not implemented**: Background scheduling, Celery/Redis task queues, and off-hours assembly are future-direction items only.
  - **Provider catalog**: Seeded from `DAILY_NEWSLETTER_PROVIDER_CATALOG` in `app/crud/care_circle.py` (32 providers defined). There are 43 provider directories under `app/services/care_circle/providers/`; not all are registered in the catalog seed.
  - **Family provider config endpoints**: `GET/PUT /family/patients/{id}/provider-configs` and `PUT /family/patients/{id}/provider-configs/{key}` are implemented and persist per-patient enablement and custom parameters.
  - **Response envelope**: All responses use `ApiResponse.success_response(...)` or `ApiResponse.error_response(...)` from `app/schemas/base.py`.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CareCircle Backend                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Router Layer (routers/care_circle.py)         │   │
│  │                                                                      │   │
│  │  GET    /care-circle/providers                                       │   │
│  │  PUT    /care-circle/providers/{provider_key}                        │   │
│  │  GET    /care-circle/family/patients                                 │   │
│  │  GET    /care-circle/family/patients/{patient_id}                    │   │
│  │  GET    /care-circle/patient/auth/catalog                            │   │
│  │  POST   /care-circle/patient/auth/login                              │   │
│  │  GET    /care-circle/patient/session/{patient_id}                    │   │
│  │  GET    /care-circle/family/patients/{id}/provider-configs           │   │
│  │  PUT    /care-circle/family/patients/{id}/provider-configs/{key}     │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        CRUD Layer (crud/care_circle.py)              │   │
│  │                                                                      │   │
│  │  - ensure_provider_catalog_seeded(db)                                │   │
│  │  - get_or_create_family_for_user(db, user)                           │   │
│  │  - list_family_patients(db, user)                                    │   │
│  │  - get_family_patient_detail(db, user, patient_id)                   │   │
│  │  - list_provider_catalog(db)                                         │   │
│  │  - get_patient_auth_catalog()                                        │   │
│  │  - update_provider_catalog(db, provider_key, enabled, visible)       │   │
│  │  - authenticate_patient_by_images(db, selected_keys)                 │   │
│  │  - get_patient_session(db, patient_id)                               │   │
│  │  - get_patient_provider_configs(db, patient_id)                      │   │
│  │  - upsert_patient_provider_config(db, patient_id, key, enabled, cfg) │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│            ┌────────────────────┼────────────────────┐                      │
│            ▼                    ▼                    ▼                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐       │
│  │  Model Layer    │  │  Service Layer  │  │  Seed Data           │       │
│  │                 │  │                 │  │                      │       │
│  │  - Family       │  │  - Session      │  │  - Provider Catalog  │       │
│  │  - Membership   │  │    Assembler    │  │  - Default Patients  │       │
│  │  - Patient      │  │                 │  │  - Auth Catalog      │       │
│  │  - Provider     │  │  - Provider     │  │                      │       │
│  │  - ContentCard  │  │    Base         │  │                      │       │
│  │  - RunLog       │  │                 │  │                      │       │
│  │  - PatientConfig│  │                 │  │                      │       │
│  │  - SessionOutput│  │                 │  │                      │       │
│  └─────────────────┘  └─────────────────┘  └──────────────────────┘       │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Provider Architecture                         │   │
│  │                                                                      │   │
│  │  BaseCareCircleProvider (abstract)                                   │   │
│  │       │                                                              │   │
│  │       ├── JokeProvider                                                 │   │
│  │       ├── DailyQuoteProvider                                           │   │
│  │       ├── WeatherProvider                                              │   │
│  │       ├── GridlessCrosswordProvider                                    │   │
│  │       ├── GentleExerciseProvider                                       │   │
│  │       ├── SimpleRecipeProvider                                         │   │
│  │       ├── SongOfTheDayProvider                                         │   │
│  │       ├── ... (32 catalog-registered, 43 directories exist)            │   │
│  │                                                                      │   │
│  │  Each provider:                                                       │   │
│  │  - provider_key: str                                                  │   │
│  │  - is_safe_for_patient: bool                                          │   │
│  │  - execute(patient_profile) → Dict[str, Any]                          │   │
│  │  - _generate_payload(patient_profile) → Dict[str, Any]                │   │
│  │  - _build_fallback_payload(patient_profile, error) → Dict[str, Any]   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Session Assembly Flow                         │   │
│  │                                                                      │   │
│  │  1. Fetch patient profile                                            │   │
│  │  2. Query enabled, patient-visible providers from catalog            │   │
│  │  3. Load per-patient provider configs (overrides/disables)           │   │
│  │  4. For each active provider:                                        │   │
│  │     a. Load provider class dynamically                               │   │
│  │     b. Check is_safe_for_patient flag                                │   │
│  │     c. Execute provider with patient config                          │   │
│  │     d. Build content card from result                                │   │
│  │  5. Delete old cards, insert new cards                               │   │
│  │  6. Return patient session with highlights                           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/care-circle/providers` | User | List provider catalog |
| PUT | `/api/v1/care-circle/providers/{provider_key}` | User | Update provider settings |
| GET | `/api/v1/care-circle/family/patients` | User | List family patients |
| GET | `/api/v1/care-circle/family/patients/{patient_id}` | User | Get patient detail |
| GET | `/api/v1/care-circle/patient/auth/catalog` | None | Get auth image catalog |
| POST | `/api/v1/care-circle/patient/auth/login` | None | Patient image-based login |
| GET | `/api/v1/care-circle/patient/session/{patient_id}` | None | Get patient daily session |
| GET | `/api/v1/care-circle/family/patients/{id}/provider-configs` | User | List patient provider configs |
| PUT | `/api/v1/care-circle/family/patients/{id}/provider-configs/{key}` | User | Upsert patient provider config |

Notes:
- All current router responses are wrapped in `ApiResponse.success_response(...)` or `ApiResponse.error_response(...)`.
- `GET /api/v1/care-circle/patient/session/{patient_id}` currently triggers on-demand regeneration before reading the patient session payload back from the database.

---

## 4. Data Model

### 4.1 Database Tables

```sql
-- CareCircle Families
care_circle_families (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_by_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Family Memberships
care_circle_family_memberships (
    id SERIAL PRIMARY KEY,
    family_id INT REFERENCES care_circle_families(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'owner' NOT NULL,
    is_primary BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(family_id, user_id)
);

-- Patient Profiles
care_circle_patient_profiles (
    id SERIAL PRIMARY KEY,
    family_id INT REFERENCES care_circle_families(id) ON DELETE CASCADE,
    created_by_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    display_name VARCHAR(255) NOT NULL,
    stage VARCHAR(50) DEFAULT 'moderate' NOT NULL, -- 'early', 'mild', 'moderate', 'severe'
    access_state VARCHAR(50) DEFAULT 'active' NOT NULL,
    timezone VARCHAR(100) DEFAULT 'America/Chicago' NOT NULL,
    delivery_time VARCHAR(20),
    delivery_days JSONB DEFAULT '[]' NOT NULL,
    auth_image_keys JSONB DEFAULT '[]' NOT NULL,
    preferences JSONB DEFAULT '{}' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Provider Catalog
care_circle_provider_catalog (
    id SERIAL PRIMARY KEY,
    provider_key VARCHAR(120) UNIQUE NOT NULL,
    label VARCHAR(255) NOT NULL,
    icon VARCHAR(20),
    category VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE NOT NULL,
    display_order INT DEFAULT 0 NOT NULL,
    patient_visible BOOLEAN DEFAULT TRUE NOT NULL,
    family_visible BOOLEAN DEFAULT TRUE NOT NULL,
    source_app VARCHAR(100) DEFAULT 'daily_newsletter' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Patient Content Cards
care_circle_patient_content_cards (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES care_circle_patient_profiles(id) ON DELETE CASCADE,
    provider_key VARCHAR(120) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    card_kind VARCHAR(50) DEFAULT 'family' NOT NULL,
    display_order INT DEFAULT 0 NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Provider Run Logs
care_circle_provider_run_logs (
    id SERIAL PRIMARY KEY,
    provider_key VARCHAR(120) NOT NULL,
    patient_id INT REFERENCES care_circle_patient_profiles(id) ON DELETE SET NULL,
    family_id INT REFERENCES care_circle_families(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'succeeded' NOT NULL,
    error_message TEXT,
    execution_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Patient Provider Configs
care_circle_provider_patient_configs (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES care_circle_patient_profiles(id) ON DELETE CASCADE,
    provider_key VARCHAR(120) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    schedule_expression VARCHAR(100),
    custom_parameters JSONB DEFAULT '{}' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(patient_id, provider_key)
);

-- Provider Session Outputs
care_circle_provider_session_outputs (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES care_circle_patient_profiles(id) ON DELETE CASCADE,
    provider_key VARCHAR(120) NOT NULL,
    run_log_id INT REFERENCES care_circle_provider_run_logs(id) ON DELETE SET NULL,
    output_json JSONB NOT NULL,
    session_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 SQLAlchemy Models

See [`app/models/care_circle.py`](app/models/care_circle.py) for full model definitions.

Key Models:
- `CareCircleFamily`: Family group container
- `CareCircleFamilyMembership`: User-to-family relationship
- `CareCirclePatientProfile`: Patient profile with preferences
- `CareCircleProviderCatalog`: Available content providers
- `CareCirclePatientContentCard`: Daily content cards for patients
- `CareCircleProviderRunLog`: Provider execution logging
- `CareCircleProviderPatientConfig`: Per-patient provider configuration
- `CareCircleProviderSessionOutput`: Provider output storage

---

## 5. Provider Architecture

### 5.1 Base Provider Interface

```python
class BaseCareCircleProvider:
    provider_key: str = "base"
    is_safe_for_patient: bool = False

    def __init__(self, patient_config: Optional[Dict[str, Any]] = None):
        self.patient_config = patient_config or {}

    async def execute(self, patient_profile: Any) -> Dict[str, Any]:
        # Safety wrapper around _generate_payload
        # Returns: {"success": bool, "provider_key": str, "data": Dict}

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        # Implemented by subclass
        raise NotImplementedError

    def _build_fallback_payload(self, patient_profile: Any, error: str) -> Dict[str, Any]:
        # Returns safe fallback payload on error
```

### 5.2 Provider Categories

| Category | Providers | Description |
|----------|-----------|-------------|
| core | weather, daily_quote, daily_affirmation, world_news, family_greeting | Essential daily content |
| wellbeing | joke, sensory, gratitude, gentle_exercise, pen_pal_letter, personal_affirmation, activity_suggestion | Wellness content |
| memory | nostalgia, dog_photo, cat_fact, nature_scene, this_day_history, song_of_the_day, local_history | Memory stimulation |
| games | puzzle, brain_booster, ai_trivia, riddle, missing_vowels, finish_phrase, odd_one_out, word_scramble, complete_the_duo, spot_the_difference, gridless_crossword | Cognitive games |
| lifestyle | simple_recipe, hobby_spotlight | Lifestyle content |

### 5.3 Provider Registration

Providers are registered via:
1. `DAILY_NEWSLETTER_PROVIDER_CATALOG` in [`crud/care_circle.py`](app/crud/care_circle.py:33) - 32 providers defined in the seed catalog.
2. Dynamic loading in [`session_assembler.py`](app/services/care_circle/session_assembler.py:27) - uses `get_provider_class()` to import `app.services.care_circle.providers.{key}.provider` and instantiate `{CamelKey}Provider`.
3. File structure: `app/services/care_circle/providers/{provider_key}/provider.py` - 43 provider directories exist; only those in the seed catalog are loaded during session assembly.

### 5.4 Current Constraints

- **No background scheduling**: Session assembly runs synchronously on each `GET /patient/session/{id}` call. This is intentional for current stabilization but should move to Celery/Redis for production scale.
- **Sequential execution**: Providers run one at a time. `asyncio.gather()` is mentioned in code comments as a future optimization.
- **No run logging yet**: `CareCircleProviderRunLog` model exists but session assembler does not write run logs during assembly.
- **No session output storage**: `CareCircleProviderSessionOutput` model exists but is not populated by current assembly flow.

---

## 6. Session Assembly Flow

```
assemble_daily_patient_session(db, patient_id)
    │
    ├── Fetch patient profile
    │   └── Return False if patient not found or archived
    │
    ├── Query enabled, patient-visible providers from catalog
    │
    ├── Load per-patient provider configs
    │   └── Build config_map for overrides
    │
    ├── Filter active providers
    │   ├── Skip if explicitly disabled by family
    │   ├── Load provider class dynamically
    │   └── Skip if not is_safe_for_patient
    │
    ├── Execute providers sequentially
    │   ├── Call provider.execute(patient)
    │   └── Build CareCirclePatientContentCard from result
    │
    ├── Delete old cards for patient
    │
    ├── Insert new cards
    │
    └── Commit and return True
```

---

## 7. Unit Tests

### 7.1 Existing Tests

| Test File | Coverage |
|-----------|----------|
| `tests/unit/care_circle/test_care_circle_unit.py` | CRUD operations, family management |
| `tests/unit/care_circle/test_care_circle_providers.py` | Provider execution |
| `tests/unit/care_circle/test_care_circle_provider_registry_unit.py` | Provider registration |
| `tests/unit/care_circle/test_all_imported_providers.py` | Provider import validation |
| `tests/integration/care_circle/test_care_circle_assembly_integration.py` | Session assembly |
| `tests/integration/care_circle/test_patient_auth_login_integration.py` | Patient auth |

### 7.2 Test Coverage Summary

| Area | Unit Tests | Integration Tests |
|------|------------|-------------------|
| Family Management | ✅ | ✅ |
| Patient CRUD | ✅ | ✅ |
| Provider Catalog | ✅ | ✅ |
| Patient Auth | ✅ | ✅ |
| Session Assembly | Partial | ✅ |
| Provider Configs | Partial | Partial |

### 7.3 Recommended Additional Tests

```python
# tests/unit/care_circle/test_patient_provider_config_unit.py
def test_upsert_patient_provider_config_creates_new():
def test_upsert_patient_provider_config_updates_existing():
def test_get_patient_provider_configs_returns_all():

# tests/unit/care_circle/test_session_assembler_unit.py
def test_assemble_session_with_no_providers():
def test_assemble_session_with_disabled_provider():
def test_assemble_session_with_unsafe_provider():
def test_assemble_session_with_custom_config():

# tests/unit/care_circle/test_provider_base_unit.py
def test_provider_execute_returns_success_on_valid():
def test_provider_execute_returns_fallback_on_error():
def test_build_fallback_payload_structure():
```

---

## 8. Integration Tests

### 8.1 Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| Family Creation | Create user → Get family | Family auto-created with default patients |
| Patient Listing | Login → List patients | Returns patient list with highlights |
| Patient Detail | Login → Get patient detail | Returns patient with content cards |
| Patient Auth | Get catalog → Select images → Login | Returns patient session |
| Provider Config | Login → Update config → Verify | Config saved and reflected |
| Session Assembly | Trigger session → Get patient | New content cards generated |

---

## 9. Suggestions and Improvements

### 9.1 Immediate Improvements
1. **Add Provider Execution Scheduling**: Implement Celery/Redis for scheduled provider execution instead of on-demand.
2. **Add Provider Health Checks**: Monitor provider success rates and alert on failures.
3. **Implement Provider Output Caching**: Cache provider outputs to reduce redundant execution.
4. **Add Patient Session History**: Store historical sessions for trend analysis.

### 9.2 Architecture Improvements
1. **Add Provider Registry Pattern**: Replace dynamic import with explicit registry for better testability.
2. **Implement Provider Dependency Injection**: Allow providers to declare dependencies (LLM, external APIs).
3. **Add Provider Execution Pipeline**: Sequential → Parallel execution with dependency graph.
4. **Implement Provider Configuration Schema**: Validate provider configs against JSON schemas.

### 9.3 Testing Improvements
1. **Add Provider Mock Tests**: Test all providers with mocked LLM/external dependencies.
2. **Add Load Tests**: Test session assembly with many patients and providers.
3. **Add Chaos Tests**: Test graceful degradation when providers fail.
4. **Add Data Validation Tests**: Validate patient data against expected schemas.

### 9.4 Performance Improvements
1. **Parallel Provider Execution**: Use `asyncio.gather()` for independent providers.
2. **Provider Output Caching**: Cache outputs with TTL to reduce execution.
3. **Database Connection Pooling**: Optimize async connection pool settings.
4. **Batch Content Card Operations**: Use bulk insert for content cards.

### 9.5 Security Considerations
1. **Rate Limit Patient Auth**: Prevent brute force on image-based auth.
2. **Validate Provider Inputs**: Sanitize patient preferences before provider execution.
3. **Audit Provider Execution**: Log all provider executions for compliance.
4. **Encrypt Sensitive Preferences**: Encrypt patient preferences containing PII.

### 9.6 Scalability Considerations
1. **Horizontal Provider Scaling**: Deploy providers as separate services.
2. **Event-Driven Session Assembly**: Use message queue for session generation.
3. **Content Delivery Network**: Serve static provider assets via CDN.
4. **Database Read Replicas**: Route read queries to replicas.

### 9.7 Future Feature Ideas
1. **Provider A/B Testing**: Test different provider configurations.
2. **Patient Engagement Analytics**: Track which content cards are most engaging.
3. **Family Messaging**: Allow family members to send messages to patients.
4. **Provider Marketplace**: Allow third-party provider registration.
5. **Multi-Language Support**: Localize provider content.
6. **Voice Output**: Convert content cards to speech for patients.

---

## 10. Document Maintenance Guidance

### 10.1 Source of Truth

The following files are the **authoritative source** for CareCircle backend behavior. When this document conflicts with code, the code wins and this document should be updated:

- `app/routers/care_circle.py` - endpoint definitions and request/response shapes
- `app/crud/care_circle.py` - data access functions, seed catalog, default patients
- `app/services/care_circle/provider_base.py` - provider interface contract
- `app/services/care_circle/session_assembler.py` - session orchestration logic
- `app/models/care_circle.py` - SQLAlchemy model definitions (database schema truth)
- `app/schemas/care_circle.py` - Pydantic validation schemas

### 10.2 When to Update This Document

Update this document when any of the following change:
- New endpoints are added or existing endpoints are removed
- Response envelope structure changes
- New models or tables are added/removed
- Provider catalog seed is modified (update the count in Section 5.3)
- Session assembly flow changes (e.g., parallel execution, background scheduling)
- New provider categories or registration patterns are introduced

### 10.3 How to Update Safely

1. Run the relevant test suite first to confirm current behavior:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest tests\unit\care_circle tests\integration\care_circle -q
   ```
2. Read the actual source file, not just this document.
3. Update the specific section that changed.
4. Update the "Last reviewed" date in the Accuracy Review section.
5. If adding new endpoints, add them to the API Endpoints table (Section 3).
6. If adding models, update the Data Model section (Section 4).

### 10.4 Implementation Status Language

Use these labels consistently:
- **Fully implemented**: Code is production-ready and tested.
- **On-demand / synchronous**: Runs per-request rather than on a schedule.
- **Scaffolded**: Route or model exists but feature depth is limited.
- **Not implemented / future-direction**: Mentioned as intent but no code exists yet.
