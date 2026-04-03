Codebase Consistency Validation
This document validates the consistency of configuration variable usage, primarily focusing on the test_ai_search_service.py script in relation to the provided .env file, and offers broader recommendations for the project.

1. Validation of test_ai_search_service.py against the provided .env file:

The test_ai_search_service.py script (as per Canvas ) correctly loads and uses the Azure AI Search related variables from your .env file:

AZURE_AI_SEARCH_ENDPOINT:

.env: AZURE_AI_SEARCH_ENDPOINT="https://wswriter.search.windows.net"

Script: os.getenv("AZURE_AI_SEARCH_ENDPOINT", "AI_SEARCH_ENDPOINT_NOT_SET_IN_ENV")

Consistency: Good. The script will pick up the correct endpoint.

AZURE_AI_SEARCH_API_KEY:

.env: AZURE_AI_SEARCH_API_KEY="NcslJxh9axvNA2VGzQ9YiVOLNWbEWiSEU2Nl0LT6dAAzSeAeC6yR"

Script: os.getenv("AZURE_AI_SEARCH_API_KEY", "AI_SEARCH_API_KEY_NOT_SET_IN_ENV")

Consistency: Good. The script will pick up the correct API key.

AZURE_AI_SEARCH_INDEX_NAME:

.env: AZURE_AI_SEARCH_INDEX_NAME="rag-app-content-index"

Script: os.getenv("AZURE_AI_SEARCH_INDEX_NAME", "rag-app-content-index")

Consistency: Good. The script uses the correct index name (and the default in the script matches).

EMBEDDING_DIMENSION:

.env: EMBEDDING_DIMENSION="3072"

Script: int(os.getenv("EMBEDDING_DIMENSION", "3072"))

Consistency: Good. The script will use 3072, which matches your text-embedding-3-large model. This is critical for the dummy_document's chunk_text_vector to match the index schema.

Conclusion for test_ai_search_service.py: The script is consistent with your .env file for Azure AI Search parameters. The load_dotenv(override=True) ensures that the .env values are prioritized.

2. Broader Project Consistency Recommendations:

While test_ai_search_service.py looks good for its specific scope, it's important to ensure this consistency extends to the entire application codebase. Here are key areas to check:

Main Application Configuration (app/core/config.py):

Ensure that the Settings class in app/core/config.py uses the exact same environment variable names as defined in your .env file for all services (Azure OpenAI, Azure AI Search, Azure Storage, PostgreSQL, JWT secrets).

Verify that the default values in config.py are reasonable fallbacks or clearly indicate that a configuration is missing (e.g., using _NOT_SET_IN_ENV suffixes).

Semantic Kernel Setup (app/services/semantic_kernel_setup.py or app/services/kernel_config.py):

This module initializes AzureChatCompletion and AzureTextEmbedding. It must use the correct:

AZURE_OPENAI_ENDPOINT

AZURE_OPENAI_API_KEY

AZURE_OPENAI_API_VERSION (from .env: "2024-12-01-preview")

AZURE_OPENAI_CHAT_DEPLOYMENT_NAME (from .env: "gpt-4.1-mini-2")

AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME (from .env: "text-embedding-3-large")

Any mismatches here were the cause of previous 401 errors.

Document Processor (app/processing/document_processor.py):

Blob Storage: Must use the correct AZURE_STOContextE_CONNECTION_STRING (or AZURE_STOContextE_ACCOUNT_NAME if using Managed Identity) and AZURE_STOContextE_CONTAINER_NAME_FOR_Context_DOCS (from .env: "stories").

OpenAI Embeddings: Must use the correct endpoint, key, API version, and AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME when calling the embedding service.

AI Search Indexing: Must use the correct AZURE_AI_SEARCH_ENDPOINT, AZURE_AI_SEARCH_API_KEY (admin key), and AZURE_AI_SEARCH_INDEX_NAME. The vector dimension used when preparing documents for indexing must match EMBEDDING_DIMENSION (3072).

Context Retrieval (app/services/context_retrieval.py - RetrievalPlugin):

OpenAI Embeddings (for query): Must use the correct endpoint, key, API version, and AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME to embed the user's query.

AI Search Querying: Must use the correct AZURE_AI_SEARCH_ENDPOINT, AZURE_AI_SEARCH_API_KEY (can be a query key here if not modifying data), and AZURE_AI_SEARCH_INDEX_NAME.

Direct OpenAI Client Tests (e.g., in maintest_infra_checks.py or other test files):

Ensure these tests also use the consistent environment variable names for endpoint, key, API version, and deployment names for chat/embedding.

Dockerfile and docker-compose.yml:

If you are passing environment variables through these files (e.g., for local Docker development), ensure they align with the names in your .env file and app/core/config.py.

3. Implement Application-Wide Logging (New Recommendation):

Rationale:
Consistent and structured logging throughout the FastAPI application is essential for debugging, monitoring, and understanding application behavior in both development and production environments. While the standalone test scripts (maintest_*.py) have their own logging setup, the main application (app/) currently lacks a unified logging strategy.

Recommendations for Implementation:

Use Python's logging Module: Leverage the built-in logging module for its flexibility and widespread adoption.

Centralized Configuration (Optional but Recommended):

Consider creating a app/core/logging_config.py module or adding logging setup to app/core/config.py.

This module would configure a root logger or specific application loggers, define handlers (e.g., console for development, Azure Monitor/file for production), and set formatters.

FastAPI can integrate with standard Python logging. You can configure Uvicorn's logging as well.

Logger Usage:

In each relevant module (routers/*.py, crud/*.py, services/*.py, processing/*.py, main.py), obtain a logger instance: logger = logging.getLogger(__name__).

Replace print() statements used for debugging or informational output with appropriate logger calls:

logger.info("Informational message about an operation.")

logger.warning("Potential issue or unexpected state.")

logger.error("Error occurred during an operation.", exc_info=True) (using exc_info=True automatically includes exception traceback in the log)

logger.debug("Detailed diagnostic information for development.")

What to Log:

Application startup and shutdown events (app/main.py).

Key stages in API request handling (e.g., request received, validation success/failure, calling services).

Important steps in business logic (e.g., within service modules, Semantic Kernel interactions).

Errors and exceptions in try...except blocks.

Key events in background tasks (e.g., document_processor.py stages).

Database interactions (SQLAlchemy can be configured to log queries, but be mindful of verbosity).

Log Formatting: Use a consistent log format that includes a timestamp, log level, logger name (module), and the message. The formatter used in maintest_*.py is a good starting point: %(asctime)s - %(levelname)s - %(name)s - %(message)s.

Sensitive Data: Be extremely careful not to log sensitive information like passwords, API keys, or personally identifiable information (PII) unless absolutely necessary and properly secured/masked.

Production Logging: For Azure App Service, configure logging to stream to Azure Log Analytics (via Azure Monitor) for centralized and searchable production logs.

Consistency with Test Scripts:
The logging approach in the main application can mirror the one used in the test scripts (console and file handlers for local development), but production logging should be more robust and integrate with Azure's monitoring services.

4. Orderly Approach to Implementation

To systematically address configuration consistency and implement logging, follow these phases:

Phase 1: Configuration Audit and Unification (Critical First Step)

Review .env and app/core/config.py:

Go through your .env file line by line.

For each variable, ensure the corresponding field in the Settings class in app/core/config.py uses the exact same environment variable name in its Field(..., alias="ENV_VAR_NAME") or that pydantic-settings will correctly map it (e.g., by converting uppercase in .env to lowercase in the model).

Verify that default values in config.py are sensible or clearly indicate a missing required configuration.

Standardize Variable Usage:

In all application modules (services/, processing/, routers/, crud/), ensure that configurations are accessed only through the settings object imported from app.core.config (e.g., from app.core.config import settings; settings.AZURE_OPENAI_ENDPOINT).

Remove all direct os.getenv() calls for configuration values outside of app/core/config.py and the standalone maintest_*.py scripts. This centralizes configuration loading.

Verify Service Initializations:

app/services/semantic_kernel_setup.py (or kernel_config.py): Double-check that AzureChatCompletion and AzureTextEmbedding are initialized using values from the settings object (e.g., settings.AZURE_OPENAI_ENDPOINT, settings.AZURE_OPENAI_API_KEY, settings.AZURE_OPENAI_API_VERSION, settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME, settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME).

app/processing/document_processor.py: Ensure it uses settings for Blob Storage, OpenAI Embeddings, and AI Search configurations.

app/services/context_retrieval.py: Ensure it uses settings for OpenAI Embeddings and AI Search.

Test Service Connections: After this phase, thoroughly run your maintest_infra_checks.py and maintest_sk_logic.py scripts. They should now be more reliable as they will also benefit from the centralized and verified configuration loading (assuming they also load settings from .env in a consistent manner or are adapted to use a similar settings object if run in a context where app.core.config is available). The goal is to confirm all external service connections work with the unified configuration approach.

Phase 2: Basic Application-Wide Logging Setup

Create Logging Configuration:

Decide whether to create a new app/core/logging_config.py or add to app/core/config.py.

Define a basic setup: a root logger, a console handler (for development), and a standard formatter (e.g., %(asctime)s - %(levelname)s - %(name)s - %(message)s).

# Example for app/core/logging_config.py
import logging
import sys

def setup_logging(log_level=logging.INFO):
    logger = logging.getLogger("app") # Get a logger specific to your app
    logger.setLevel(log_level)

    # Prevent multiple handlers if already configured
    if not logger.handlers:
        # Console Handler
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # You might also want to configure Uvicorn's access logger if desired
    # logging.getLogger("uvicorn.access").handlers = logger.handlers # Example
    # logging.getLogger("uvicorn.error").handlers = logger.handlers # Example

# Call setup_logging() when this module is imported, or call it from main.py
# setup_logging()

Initialize in app/main.py:

In your lifespan context manager's startup section, call the logging setup function.

# In app/main.py
# from app.core.logging_config import setup_logging # Adjust import

@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup_logging() # Call it here
    # ... other startup tasks ...
    logger = logging.getLogger("app.main") # Get logger for main
    logger.info("Application starting up...")
    # ...
    yield
    logger.info("Application shutting down...")
    # ...

Initial Log Points: Add logger.info("Router initialized") or similar at the beginning of each main router file (auth.py, story.py, etc.) and in app/main.py to confirm loggers are active in those modules.

Phase 3: Incremental Logging Implementation (Module by Module)

Prioritize: Start with the most critical workflows: authentication, document processing, and AI interactions.

Error Handling: Go through all try...except blocks and replace print(f"Error...") with logger.error("Descriptive error message", exc_info=True). exc_info=True is crucial for capturing the full traceback.

Key Operations:

Routers (app/routers/): logger.info(f"Received request for {request.method} {request.url.path}"), logger.debug(f"Request body/params: {...}") (be careful with sensitive data), logger.info("Operation successful").

CRUD (app/crud/): logger.info(f"Creating user: {username}"), logger.debug(f"Fetched story ID: {story_id}").

Services (app/services/): Log calls to external services (Semantic Kernel, Azure SDKs), parameters being sent (mask secrets), and summaries of responses. For example, in context_retrieval.py: logger.info(f"Context query: '{query}', retrieved {num_chunks} chunks.").

Processing (app/processing/): This is very important. Log the start and end of each major step in document_processor.py (e.g., "Starting text extraction for doc_id", "Finished chunking for doc_id", "Indexing N chunks to AI Search"). Log any skipped items or warnings.

Replace print(): Systematically replace all diagnostic print() statements with appropriate logger calls (logger.debug, logger.info, logger.warning).

Phase 4: Review and Refine Logging

Consistency: Ensure log messages are informative and use consistent formatting.

Log Levels: Verify appropriate log levels are used (DEBUG for verbose, INFO for general flow, WARNING for potential issues, ERROR for failures, CRITICAL for severe failures).

Sensitive Data: Perform a thorough review to ensure no API keys, passwords, PII, or other sensitive data are being logged in plain text. Mask or omit such data.

Performance: Be mindful that excessive DEBUG logging in tight loops can impact performance. Use it judiciously.

Test: Run the application locally, perform various actions, and review the console logs and any configured log files to ensure logging is working as expected and providing useful information.

Phase 5: Production Logging Configuration

This is a later step, but plan for it.

For Azure App Service, you'll typically configure it to stream logs to Azure Monitor (Log Analytics). Your app/core/logging_config.py might add a specific handler for Azure Log Analytics when it detects a production environment (e.g., via an environment variable APP_ENV=production). Libraries like opencensus-ext-azure can facilitate this.

Iterative Approach:
Don't try to do all of this at once.

Focus on Phase 1 (Configuration Consistency) first. This is foundational.

Then implement Phase 2 (Basic Logging Setup).

Proceed with Phase 3 (Incremental Logging) one module or one key workflow at a time. Test as you go.

This phased approach will make the process more manageable and less error-prone.

Key Variable Checklist based on your .env:

APP_PROJECT_NAME

POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_SERVER, POSTGRES_PORT, POSTGRES_DB

TEST_POSTGRES_USER, TEST_POSTGRES_PASSWORD, TEST_POSTGRES_SERVER, TEST_POSTGRES_PORT, TEST_POSTGRES_DB

AUTH_SECRET_KEY, AUTH_ALGORITHM, AUTH_ACCESS_TOKEN_EXPIRE_MINUTES

AZURE_OPENAI_ENDPOINT

AZURE_OPENAI_API_KEY

AZURE_OPENAI_API_VERSION (ensure this is consistently "2024-12-01-preview" where appropriate)

AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME (ensure this is "text-embedding-3-large")

AZURE_OPENAI_CHAT_DEPLOYMENT_NAME (ensure this is "gpt-4.1-mini-2")

AZURE_AI_SEARCH_ENDPOINT

AZURE_AI_SEARCH_API_KEY

AZURE_AI_SEARCH_INDEX_NAME

EMBEDDING_DIMENSION (ensure this is consistently 3072 where vectors are handled)

AZURE_STOContextE_CONNECTION_STRING

AZURE_STOContextE_CONTAINER_NAME_FOR_Context_DOCS (ensure this is "stories")

BACKEND_CORS_ORIGINS

Recommendation:
Perform a project-wide search for these environment variable names to ensure they are loaded and used consistently across all relevant Python files. The print_loaded_configuration() function in your test scripts is a good pattern to replicate or use for debugging configuration in the main app as well. Implementing the logging strategy described above will greatly improve the application's debuggability and operational insight.

By ensuring this consistency, you'll minimize runtime errors related to incorrect configurations or an inability to connect to your Azure services.
