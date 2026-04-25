# Scheduler Module

This module runs the background scheduler service for Ink & Quill, with the current focus on Care Circle automation.

It is a standalone FastAPI app that:

- starts an `APScheduler` `AsyncIOScheduler`
- persists scheduled jobs in PostgreSQL
- registers task functions from `app/scheduler/tasks/`
- exposes HTTP endpoints for health, status, listing jobs, manual runs, pause/resume, and rescheduling
- serves a small static scheduler UI from `app/scheduler/static/` when present

## Main Flow

The scheduler starts in [main.py](/C:/Code/inkandquill/inkquill/app/scheduler/main.py).

Startup flow:

1. Build the APScheduler instance with a PostgreSQL-backed `SQLAlchemyJobStore`.
2. Import the task modules so each `@register_task(...)` decorator runs.
3. Read all registered tasks from the in-memory registry.
4. Add every `enabled_by_default` task to APScheduler using its cron expression.
5. Start the scheduler.
6. Immediately kick off `care_circle.precache_providers` once on startup to warm cache for today plus the next 3 days.

Shutdown flow:

1. Stop the scheduler without waiting for long-running jobs to finish.
2. Clear `app.state.scheduler`.

## Core Pieces

- [main.py](/C:/Code/inkandquill/inkquill/app/scheduler/main.py): FastAPI app, lifespan startup/shutdown, router wiring, static UI.
- [scheduler_engine.py](/C:/Code/inkandquill/inkquill/app/scheduler/scheduler_engine.py): creates the APScheduler instance and PostgreSQL job store.
- [registry.py](/C:/Code/inkandquill/inkquill/app/scheduler/registry.py): simple in-memory task registry populated by decorators.
- [logging.py](/C:/Code/inkandquill/inkquill/app/scheduler/logging.py): structured task and job-operation logging helpers.
- [schemas.py](/C:/Code/inkandquill/inkquill/app/scheduler/schemas.py): API response and request models.
- [routers/health.py](/C:/Code/inkandquill/inkquill/app/scheduler/routers/health.py): health and task status endpoints.
- [routers/jobs.py](/C:/Code/inkandquill/inkquill/app/scheduler/routers/jobs.py): job list, manual run, pause, resume, and reschedule endpoints.
- [tasks/](/C:/Code/inkandquill/inkquill/app/scheduler/tasks): registered scheduled jobs.

## How Task Registration Works

Tasks are regular async functions decorated with `@register_task(...)`.

The decorator stores a `TaskDefinition` in a module-level registry with:

- `key`: stable scheduler/job identifier
- `name`: operator-friendly label
- `func`: async function APScheduler runs
- `default_cron`: default cron schedule
- `description`: human-readable purpose
- `enabled_by_default`: whether startup should schedule it automatically
- `max_instances`: concurrent run limit
- `misfire_grace_time`: late-run grace window in seconds

Important detail: the registry is in-memory only. Importing the task modules at startup is what populates it.

## How Scheduling Persistence Works

The scheduler uses `SQLAlchemyJobStore` with a PostgreSQL connection built from the main app settings:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_SERVER`
- `POSTGRES_PORT`
- `POSTGRES_DB`

Scheduled job metadata is stored in the `scheduled_jobs` table. This means the scheduler can preserve APScheduler job definitions across service restarts.

The scheduler timezone comes from `settings.TIMEZONE`.

## Current Scheduled Tasks

These are the tasks currently imported and scheduled by default.

| Task Key | Default Cron | Purpose |
| --- | --- | --- |
| `care_circle.precache_providers` | `0 2 * * *` | Pre-generates only missing provider cache entries for active patients for today plus the next 3 days. |
| `care_circle.daily_session` | `0 6 * * *` | Builds the full daily Care Circle session for each active patient and records job status. |
| `care_circle.daily_newsletter_pdf` | `0 7 * * *` | Ensures `newsletter.html` and `newsletter.pdf` exist for each active patient. |
| `care_circle.daily_newsletter` | `0 8 * * *` | Sends the full daily newsletter to each active patient. |
| `care_circle.mini_newsletter` | `0 9 * * *` | Sends a smaller email assembled from 5 cached provider outputs. |
| `scheduler.cleanup_old_run_logs` | `0 3 * * 0` | Deletes old `CareCircleProviderRunLog` rows older than 90 days. |
| `scheduler.diagnostic_dir_list` | `*/5 * * * *` | Diagnostic task that runs `dir` and logs the result. Primarily useful for scheduler verification. |

## Task Details

### `care_circle.precache_providers`

Defined in [tasks/care_circle_precache.py](/C:/Code/inkandquill/inkquill/app/scheduler/tasks/care_circle_precache.py).

What it does:

- finds active patients
- finds patient-visible, enabled provider catalog entries
- respects patient-level provider disablement
- skips providers already cached
- executes only missing providers
- saves results into the Care Circle provider cache

This task is also launched once immediately at scheduler startup, independent of the 2:00 AM cron.

### `care_circle.daily_session`

Defined in [tasks/care_circle_session.py](/C:/Code/inkandquill/inkquill/app/scheduler/tasks/care_circle_session.py).

What it does:

- finds active patients
- resolves the owning user for job status tracking
- creates a `job_status` record
- runs `assemble_daily_patient_session(...)`
- marks the job as completed or failed

This is the main pre-generation path for full daily Care Circle content.

### `care_circle.daily_newsletter_pdf`

Defined in [tasks/care_circle_newsletter_pdf.py](/C:/Code/inkandquill/inkquill/app/scheduler/tasks/care_circle_newsletter_pdf.py).

What it does:

- finds active patients
- checks whether newsletter HTML already exists for the target date
- assembles the session if needed
- calls the PDF service to generate newsletter artifacts

This task depends on the newsletter render/PDF pipeline being available in the runtime environment.

### `care_circle.daily_newsletter`

Defined in [tasks/care_circle_newsletter.py](/C:/Code/inkandquill/inkquill/app/scheduler/tasks/care_circle_newsletter.py).

What it does:

- finds active patients
- calls `deliver_newsletter_to_patient(...)` for each patient
- records per-patient success/failure results

This is the scheduled full email delivery path.

### `care_circle.mini_newsletter`

Defined in [tasks/care_circle_mini_newsletter.py](/C:/Code/inkandquill/inkquill/app/scheduler/tasks/care_circle_mini_newsletter.py).

What it does:

- reads cached provider JSON for the day
- excludes header/footer cache entries
- randomly selects 5 provider blocks
- renders a fresh header and footer
- sends the smaller email version

This task relies on the provider cache being populated first, so its current 9:00 AM schedule intentionally comes after precache and session assembly.

### `scheduler.cleanup_old_run_logs`

Defined in [tasks/cleanup.py](/C:/Code/inkandquill/inkquill/app/scheduler/tasks/cleanup.py).

What it does:

- deletes `CareCircleProviderRunLog` rows older than 90 days
- commits the cleanup in the database

### `scheduler.diagnostic_dir_list`

Defined in [tasks/diagnostic.py](/C:/Code/inkandquill/inkquill/app/scheduler/tasks/diagnostic.py).

What it does:

- runs `cmd.exe /c dir`
- logs the result length and exit code

This is a diagnostic task rather than business functionality. Because it is still `enabled_by_default=True`, it currently runs every 5 minutes unless explicitly removed or changed.

## HTTP API

The scheduler app exposes these endpoints under the `/scheduler` prefix.

### Health and Status

- `GET /scheduler/health`
  - returns overall health, whether the scheduler is running, number of registered tasks, and number of scheduled jobs
- `GET /scheduler/status`
  - returns all registered tasks with default cron and the currently known next run time

### Job Operations

- `GET /scheduler/jobs`
  - lists scheduled APScheduler jobs
- `POST /scheduler/jobs/{task_key}/run`
  - manually executes the task function immediately
  - optional query param: `reference_date=YYYY-MM-DD`
- `POST /scheduler/jobs/{task_key}/pause`
  - pauses an existing scheduled job
- `POST /scheduler/jobs/{task_key}/resume`
  - resumes a paused job
- `POST /scheduler/jobs/{task_key}/reschedule`
  - accepts JSON like `{ "cron": "0 10 * * *" }`

## Logging

The scheduler uses structured logging helpers from [logging.py](/C:/Code/inkandquill/inkquill/app/scheduler/logging.py).

Task execution logs include:

- task start
- task completion
- task failure
- duration in seconds
- task key and task name

Job operation logs include:

- trigger
- pause
- resume
- reschedule

## Running the Scheduler

Typical local entrypoint:

```powershell
.\.venv\Scripts\python.exe -m app.scheduler.main
```

Or with Uvicorn directly:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.scheduler.main:app --host 0.0.0.0 --port 8001
```

Relevant config values in [app/core/config.py](/C:/Code/inkandquill/inkquill/app/core/config.py):

- `SCHEDULER_PORT`
- `SCHEDULER_ENABLED`
- `SCHEDULER_MISFIRE_GRACE_TIME`
- `TIMEZONE`
- PostgreSQL connection settings used by the job store

## Test Coverage

There is existing scheduler coverage in:

- `tests/unit/scheduler/`
- `tests/integration/scheduler/`

This includes coverage for:

- task registry behavior
- health/status endpoints
- job listing
- manual trigger/pause/resume/reschedule flows
- at least part of the Care Circle session task path

## Operational Notes

- The task registry is not auto-discovered. New task modules must be imported in [main.py](/C:/Code/inkandquill/inkquill/app/scheduler/main.py) or they will not be scheduled.
- The startup warm-cache run is separate from APScheduler persistence, so it will fire each time the service boots.
- `care_circle.mini_newsletter` depends on cache artifacts already existing.
- `scheduler.diagnostic_dir_list` is currently a live scheduled task, not just a test helper.

## Adding a New Task

1. Create an async function in `app/scheduler/tasks/`.
2. Decorate it with `@register_task(...)`.
3. Give it a stable `key` and valid cron expression.
4. Import the module in [main.py](/C:/Code/inkandquill/inkquill/app/scheduler/main.py) so registration happens at startup.
5. Add or update unit/integration tests if the task or API behavior changes.
