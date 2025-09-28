# maintest_infra_checks.py
# Standalone test script for:
# - Basic password utility testing
# - Database connection testing
# - Configuration verification
# - Direct Azure OpenAI embedding test
# - Azure Storage Account connection, write, read, and delete test
# Loads configuration from a .env file or system environment variables.
# Logs output to a timestamped file.

import os
import asyncio
import uuid
from typing import Optional, List, Any
from passlib.context import CryptContext
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from openai import AsyncAzureOpenAI, APIError
import logging
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
# Azure AI Search imports are no longer needed here
# from azure.search.documents.aio import SearchClient
# from azure.search.documents.indexes.aio import SearchIndexClient
# from azure.core.credentials import AzureKeyCredential

# --- Setup Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_name = f'maintest_infra_checks_{current_time_str}.log' # Unique log file name
file_handler = logging.FileHandler(log_file_name, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# --- Load Environment Variables from .env file ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
logger.info(f"Attempting to load .env file from: {dotenv_path}")
if os.path.exists(dotenv_path):
    loaded_from_env_file = load_dotenv(dotenv_path=dotenv_path, override=True)
    if loaded_from_env_file:
        logger.info(f"Successfully loaded variables from: {dotenv_path}")
    else:
        logger.warning(f".env file found at {dotenv_path}, but no variables were loaded.")
else:
    logger.info(f".env file not found. Relying on system environment variables or script defaults.")

# --- Password Hashing Utilities ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
def verify_password_test(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash_test(password: str) -> str:
    return pwd_context.hash(password)

# --- Configuration Loading ---
logger.info("--- Loading Configuration for Infrastructure Checks ---")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "ENDPOINT_NOT_SET_IN_ENV")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "API_KEY_NOT_SET_IN_ENV")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "EMBEDDING_DEPLOYMENT_NOT_SET_IN_ENV")

DB_USER = os.getenv("POSTGRES_USER", "DB_USER_NOT_SET_IN_ENV")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "DB_PASSWORD_NOT_SET_IN_ENV")
DB_HOST = os.getenv("POSTGRES_SERVER", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "DB_NAME_NOT_SET_IN_ENV")
DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "STORAGE_CONNECTION_STRING_NOT_SET_IN_ENV")
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "STORAGE_ACCOUNT_NAME_NOT_SET_IN_ENV")
TEST_STORAGE_CONTAINER_NAME = os.getenv("TEST_STORAGE_CONTAINER_NAME", "maintest-blob-container")

# Azure AI Search configuration is no longer needed in this file
# AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "AI_SEARCH_ENDPOINT_NOT_SET_IN_ENV")
# AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY", "AI_SEARCH_API_KEY_NOT_SET_IN_ENV")
# AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME", "rag-app-content-index")


def print_loaded_configuration():
    logger.info("\n--- Loaded Configuration Values (maintest_infra_checks.py) ---")
    logger.info(f"AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
    logger.info(f"AZURE_OPENAI_API_KEY: {'********' if AZURE_OPENAI_API_KEY and not AZURE_OPENAI_API_KEY.endswith('_NOT_SET_IN_ENV') else AZURE_OPENAI_API_KEY}")
    logger.info(f"AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION}")
    logger.info(f"EMBEDDING_DEPLOYMENT_NAME: {EMBEDDING_DEPLOYMENT_NAME}")
    logger.info(f"DB_USER: {DB_USER}")
    logger.info(f"DB_PASSWORD: {'********' if DB_PASSWORD and not DB_PASSWORD.endswith('_NOT_SET_IN_ENV') else DB_PASSWORD}")
    logger.info(f"DB_HOST: {DB_HOST}")
    logger.info(f"DB_PORT: {DB_PORT}")
    logger.info(f"DB_NAME: {DB_NAME}")
    logger.info(f"AZURE_STORAGE_CONNECTION_STRING: {'********' if AZURE_STORAGE_CONNECTION_STRING and not AZURE_STORAGE_CONNECTION_STRING.endswith('_NOT_SET_IN_ENV') else AZURE_STORAGE_CONNECTION_STRING}")
    logger.info(f"AZURE_STORAGE_ACCOUNT_NAME: {AZURE_STORAGE_ACCOUNT_NAME}")
    logger.info(f"TEST_STORAGE_CONTAINER_NAME: {TEST_STORAGE_CONTAINER_NAME}")
    # logger.info(f"AZURE_AI_SEARCH_ENDPOINT: {AZURE_AI_SEARCH_ENDPOINT}") # Removed
    # logger.info(f"AZURE_AI_SEARCH_API_KEY: {'********' if AZURE_AI_SEARCH_API_KEY and not AZURE_AI_SEARCH_API_KEY.endswith('_NOT_SET_IN_ENV') else AZURE_AI_SEARCH_API_KEY}") # Removed
    # logger.info(f"AZURE_AI_SEARCH_INDEX_NAME: {AZURE_AI_SEARCH_INDEX_NAME}") # Removed
    logger.info(f"LOG_FILE_NAME: {log_file_name}")
    logger.info("---------------------------------")

def test_password_hashing():
    logger.info("\n--- Testing Password Utilities ---")
    password = "mysecretpassword123"
    hashed_password = get_password_hash_test(password)
    logger.info(f"Original Password: {password}")
    logger.info(f"Hashed Password (first characters): {hashed_password[:30]}...")
    logger.info(f"Hash scheme used: {pwd_context.identify(hashed_password)}")
    assert isinstance(hashed_password, str)
    assert hashed_password != password
    assert len(hashed_password) > 0
    logger.info("Password hashing test passed.")
    assert verify_password_test(password, hashed_password) is True
    logger.info("Correct password verification passed.")
    incorrect_password = "wrongpassword"
    assert verify_password_test(incorrect_password, hashed_password) is False
    logger.info("Incorrect password verification passed.")
    logger.info("--- Password Utility Tests Complete ---")

async def test_database_connection():
    logger.info("\n--- Testing Database Connection ---")
    if any(val.endswith("_NOT_SET_IN_ENV") for val in [DB_USER, DB_PASSWORD, DB_NAME]):
        logger.warning("WARNING: DB credentials use placeholders. Skipping live DB test.")
        logger.info("--- Database Connection Test Skipped ---")
        return
    engine = None
    try:
        engine = create_async_engine(DATABASE_URL_TEST)
        async with engine.connect() as connection:
            result = await connection.execute(sqlalchemy.text("SELECT 1"))
            assert result.scalar_one() == 1
            logger.info("SUCCESS: Successfully connected to PostgreSQL and executed 'SELECT 1'.")
        logger.info("--- Database Connection Test Complete ---")
    except Exception as e:
        logger.error(f"FAILURE: Could not connect to PostgreSQL. Error: {type(e).__name__}: {e}")
        logger.info("--- Database Connection Test Failed ---")
    finally:
        if engine: await engine.dispose()

async def test_azure_storage_operations():
    logger.info("\n--- Testing Azure Blob Storage Operations ---")
    if AZURE_STORAGE_CONNECTION_STRING.endswith("_NOT_SET_IN_ENV") and \
       AZURE_STORAGE_ACCOUNT_NAME.endswith("_NOT_SET_IN_ENV"):
        logger.warning("WARNING: Azure Storage configuration uses placeholders. Skipping storage operations test.")
        logger.info("--- Azure Storage Operations Test Skipped ---")
        return
    blob_service_client = None
    credential_for_storage_test = None
    test_blob_name = f"test-blob-infra-checks-{uuid.uuid4()}.txt"
    test_blob_content = f"Hello from maintest_infra_checks.py at {datetime.now().isoformat()}"
    try:
        if AZURE_STORAGE_CONNECTION_STRING and not AZURE_STORAGE_CONNECTION_STRING.endswith("_NOT_SET_IN_ENV"):
            logger.info("Attempting to connect to Azure Storage using Connection String.")
            blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        elif AZURE_STORAGE_ACCOUNT_NAME and not AZURE_STORAGE_ACCOUNT_NAME.endswith("_NOT_SET_IN_ENV"):
            logger.info(f"Attempting to connect to Azure Storage Account '{AZURE_STORAGE_ACCOUNT_NAME}' using DefaultAzureCredential.")
            account_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential_for_storage_test = DefaultAzureCredential()
            blob_service_client = BlobServiceClient(account_url=account_url, credential=credential_for_storage_test)
        else:
            logger.error("FAILURE: Insufficient Azure Storage configuration provided.")
            logger.info("--- Azure Storage Operations Test Failed ---")
            return
        logger.info(f"Using container: {TEST_STORAGE_CONTAINER_NAME}")
        container_client = blob_service_client.get_container_client(TEST_STORAGE_CONTAINER_NAME)
        try: await container_client.create_container()
        except Exception as ce: logger.info(f"Container '{TEST_STORAGE_CONTAINER_NAME}' likely already exists or error: {ce}")
        blob_client = container_client.get_blob_client(test_blob_name)
        await blob_client.upload_blob(test_blob_content.encode('utf-8'), overwrite=True)
        logger.info("SUCCESS: Test blob uploaded.")
        downloader = await blob_client.download_blob()
        downloaded_bytes = await downloader.readall()
        assert downloaded_bytes.decode('utf-8') == test_blob_content
        logger.info("SUCCESS: Test blob read and content verified.")
        logger.info("--- Azure Storage Operations Test Complete ---")
    except Exception as e:
        logger.error(f"FAILURE: Error during Azure Storage operations. Error: {type(e).__name__}: {e}")
        logger.info("--- Azure Storage Operations Test Failed ---")
    finally:
        if blob_service_client:
            try:
                blob_client_for_delete = blob_service_client.get_blob_client(container=TEST_STORAGE_CONTAINER_NAME, blob=test_blob_name)
                await blob_client_for_delete.delete_blob()
                logger.info("SUCCESS: Test blob deleted.")
            except ResourceNotFoundError: logger.info(f"Test blob '{test_blob_name}' not found for deletion.")
            except Exception as e_del: logger.error(f"ERROR deleting test blob '{test_blob_name}': {e_del}")
            await blob_service_client.close()
        if credential_for_storage_test: await credential_for_storage_test.close()

async def test_azure_openai_embedding_direct():
    logger.info("\n--- Testing Direct Azure OpenAI Embedding Service ---")
    if any(val.endswith("_NOT_SET_IN_ENV") for val in [AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, EMBEDDING_DEPLOYMENT_NAME]):
        logger.warning("WARNING: Azure OpenAI embedding config uses placeholders. Skipping direct embedding test.")
        logger.info("--- Direct Embedding Test Skipped ---")
        return
    aclient = None
    try:
        logger.info(f"Direct OpenAI Embedding Test - Endpoint: {AZURE_OPENAI_ENDPOINT}")
        logger.info(f"Direct OpenAI Embedding Test - API Key: {'********'}")
        logger.info(f"Direct OpenAI Embedding Test - API Version: {AZURE_OPENAI_API_VERSION}")
        logger.info(f"Direct OpenAI Embedding Test - Deployment: {EMBEDDING_DEPLOYMENT_NAME}")
        aclient = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
        )
        test_text = "This is a sample text to test embedding."
        response = await aclient.embeddings.create(input=[test_text], model=EMBEDDING_DEPLOYMENT_NAME)
        if response.data and len(response.data) > 0 and response.data[0].embedding:
            logger.info(f"SUCCESS: Generated embedding. Vector length: {len(response.data[0].embedding)}")
        else:
            logger.error("FAILURE: Embedding call succeeded but response data is not as expected.")
        logger.info("--- Direct Embedding Test Complete ---")
    except APIError as e_api:
        logger.error(f"FAILURE generating embedding directly (APIError). Status: {e_api.status_code}, Message: {e_api.message}")
        if hasattr(e_api, 'body') and e_api.body: logger.error(f"   Body: {e_api.body}")
    except Exception as e:
        logger.error(f"FAILURE generating embedding directly (General). Error: {type(e).__name__}: {e}")
    finally:
        if aclient: await aclient.close()

async def test_non_existent_user_login_attempt():
    logger.info("\n--- Testing Non-Existent User Login Attempt ---")
    if any(val.endswith("_NOT_SET_IN_ENV") for val in [DB_USER, DB_PASSWORD, DB_NAME]):
        logger.warning("WARNING: DB credentials use placeholders. Skipping non-existent user test.")
        logger.info("--- Non-Existent User Login Test Skipped ---")
        return
    engine = None
    try:
        engine = create_async_engine(DATABASE_URL_TEST)
        async with engine.connect() as connection:
            query = sqlalchemy.text("SELECT id FROM users WHERE username = :username_param")
            result = await connection.execute(query, {"username_param": "user_does_not_exist_123abc"})
            user_record = result.fetchone()
            assert user_record is None
            logger.info("SUCCESS: Non-existent user not found, as expected.")
        logger.info("--- Non-Existent User Login Test Complete ---")
    except Exception as e:
        logger.error(f"FAILURE during non-existent user test: {e}")
        logger.info("--- Non-Existent User Login Test Failed ---")
    finally:
        if engine: await engine.dispose()

async def test_existing_user_login_attempts():
    logger.info("\n--- Testing Existing User Login Attempts ---")
    if any(val.endswith("_NOT_SET_IN_ENV") for val in [DB_USER, DB_PASSWORD, DB_NAME]):
        logger.warning("WARNING: DB credentials use placeholders. Skipping existing user login test.")
        logger.info("--- Existing User Login Test Skipped ---")
        return
    test_username = "existing_test_user_argon"
    test_password = "StrongPassword123!"
    engine = None
    try:
        engine = create_async_engine(DATABASE_URL_TEST)
        async with engine.connect() as connection:
            query_select = sqlalchemy.text("SELECT hashed_password FROM users WHERE username = :u")
            user_rec_result = await connection.execute(query_select, {"u": test_username})
            user_rec = user_rec_result.fetchone()
            hashed_pw_for_test = ""
            if user_rec:
                hashed_pw_for_test = user_rec.hashed_password
            else:
                hashed_pw_for_test = get_password_hash_test(test_password)
                async with connection.begin():
                     await connection.execute(sqlalchemy.text("INSERT INTO users (username, hashed_password, email, is_active) VALUES (:u, :hp, :e, :ia)"),
                                             {"u":test_username, "hp":hashed_pw_for_test, "e":f"{test_username}@example.com", "ia":True})
                logger.info(f"Created user {test_username} for test.")

            assert verify_password_test(test_password, hashed_pw_for_test)
            logger.info(f"SUCCESS: Correct password for '{test_username}' verified.")
            assert not verify_password_test("wrongpass", hashed_pw_for_test)
            logger.info(f"SUCCESS: Incorrect password for '{test_username}' rejected.")
        logger.info("--- Existing User Login Attempts Test Complete ---")
    except Exception as e:
        logger.error(f"FAILURE during existing user login test: {type(e).__name__}: {e}")
        logger.info("--- Existing User Login Attempts Test Failed ---")
    finally:
        if engine: await engine.dispose()

async def main():
    """Runs all infrastructure and direct service check tests."""
    logger.info(f"Starting maintest_infra_checks.py script... Log file: {log_file_name}")
    print_loaded_configuration()
    test_password_hashing()
    await test_database_connection()
    await test_non_existent_user_login_attempt()
    await test_existing_user_login_attempts()
    await test_azure_storage_operations()
    # Removed Azure AI Search test from this file:
    # await test_azure_ai_search_operations() 
    await test_azure_openai_embedding_direct()
    logger.info("maintest_infra_checks.py script finished.")

if __name__ == "__main__":
    asyncio.run(main())