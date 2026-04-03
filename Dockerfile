# /story_app/Dockerfile

# --- Stage 1: Build Dependencies ---
# Use an official Python runtime as a parent image. Choose a specific version
# matching your development environment for consistency. Using slim-bullseye
# provides a smaller base image.
FROM python:3.11-slim-bullseye as builder

# Set the working directory inside the container
WORKDIR /opt/app_build

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies that might be needed by Python packages
# (e.g., build-essential for compiling C extensions, libpq-dev for psycopg2 if not using binary)
# Update package lists and install, then clean up apt cache to keep image size down.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry (or just use pip if you prefer)
# Using Poetry or another package manager can help manage dependencies more robustly.
# If using pip directly, you'd just copy requirements.txt and run pip install.
# RUN pip install --upgrade pip
# RUN pip install poetry

# Copy only the files needed for dependency installation first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./
# If using requirements.txt:
# COPY requirements.txt .

# Install dependencies using Poetry
# --no-root: Don't install the project package itself in this stage
# --no-dev: Don't install development dependencies
# --no-interaction: Don't ask interactive questions
# --no-ansi: Plain output
# RUN poetry config virtualenvs.create false && \
#     poetry install --no-root --no-dev --no-interaction --no-ansi
# If using pip:
RUN pip wheel --no-cache-dir --wheel-dir /opt/wheels -r requirements.txt


# --- Stage 2: Runtime Stage ---
# Use a slim Python base image for the final runtime container
FROM python:3.11-slim-bullseye as runtime

# Set the working directory for the application
WORKDIR /app

# Set environment variables (same as builder stage)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install runtime system dependencies (e.g., libpq5 for psycopg2 runtime)
# Only install what's needed to run the application, not build tools.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python dependencies from the builder stage's wheelhouse
# This makes the final image smaller as it doesn't contain build tools or source distributions.
COPY --from=builder /opt/wheels /opt/wheels
RUN pip install --no-cache /opt/wheels/* && rm -rf /opt/wheels

# Create a non-root user to run the application for better security
# Use a fixed UID/GID for reproducibility if needed
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup --no-create-home appuser
# Set permissions if needed for specific directories (e.g., static files if handled differently)
# RUN chown -R appuser:appgroup /app

# Copy the application code into the container
# Ensure .dockerignore is set up correctly to avoid copying unnecessary files (.git, .venv, etc.)
COPY ./app /app/app

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the application will run on (e.g., 8000)
# This should match the port Gunicorn/Uvicorn is configured to listen on.
EXPOSE 8000

# --- Define the Command to run the application ---
# Use Gunicorn as the process manager and Uvicorn for the ASGI worker.
# -w: Number of worker processes (adjust based on CPU cores, typically 2-4 * cores + 1)
# -k: Worker class (uvicorn.workers.UvicornWorker for FastAPI)
# -b: Bind address and port (0.0.0.0 makes it listen on all interfaces inside the container)
# app.main:app: Path to your FastAPI app instance (module:instance)
# --timeout: Increase timeout if requests might take longer (e.g., AI processing)
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "120", "app.main:app"]

# --- Healthcheck (Optional but Recommended) ---
# Defines how Docker can check if the container is healthy.
# Adjust the path and interval/timeout as needed.
# HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:8000/ || exit 1 # Example: Check root path
