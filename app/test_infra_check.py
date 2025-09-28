#!/usr/bin/env python3
import os
import sys
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text
from openai import AsyncAzureOpenAI
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import DefaultAzureCredential

# --- Exception for Skipped Tests ---
class SkipTest(Exception):
    pass

# --- Setup Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = f"infra_checks_{datetime.utcnow():%Y%m%dT%H%M%SZ}.log"
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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

# --- Monkey‑patch bcrypt for Passlib ---
try:
    import bcrypt, pkg_resources
    if not hasattr(bcrypt, "__about__"):
        version = pkg_resources.get_distribution("bcrypt").version
        class _BcryptAbout:
            __version__ = version
        bcrypt.__about__ = _BcryptAbout
        logger.info(f"Patched bcrypt.__about__ to version {version}")
except Exception as e:
    logger.warning(f"Could not patch bcrypt version: {e}")

# --- Config ---
DATABASE_URL           = os.getenv("DATABASE_URL_TEST", "NOT_SET")
STORAGE_ACCOUNT_URL    = os.getenv("AZURE_STORAGE_ACCOUNT_URL", "NOT_SET")
STORAGE_CONTAINER      = os.getenv("AZURE_STORAGE_CONTAINER", "$logs")
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY", "NOT_SET")
OPENAI_API_TYPE        = os.getenv("OPENAI_API_TYPE", "azure")
OPENAI_API_BASE        = os.getenv("OPENAI_API_BASE", "NOT_SET")
OPENAI_API_VERSION     = os.getenv("OPENAI_API_VERSION", "2023-05-15")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_EMBEDDING_DEPLOYMENT", "NOT_SET")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Helpers ---
async def run_db_query(sql: str, params: Dict[str, Any] = None) -> Any:
    engine: AsyncEngine = create_async_engine(DATABASE_URL, future=True)
    try:
        async with engine.connect() as conn:
            return await conn.execute(text(sql), params or {})
    finally:
        await engine.dispose()

def need_skip(value: str) -> bool:
    return value.upper().endswith("NOT_SET")

# --- Tests ---
async def test_password_hashing():
    logger.info("Running test: password hashing and verification")
    raw = "CorrectHorseBatteryStaple"
    hashed = pwd_context.hash(raw)
    assert pwd_context.verify(raw, hashed), "hash did not verify"
    return True

async def test_database_connection():
    logger.info("Running test: database connectivity")
    if need_skip(DATABASE_URL):
        raise SkipTest("DATABASE_URL_TEST not set")
    result = await run_db_query("SELECT 1")
    assert result.scalar_one() == 1, "expected scalar 1"
    return True

async def test_user_login_flow():
    logger.info("Running test: user login transaction")
    if need_skip(DATABASE_URL):
        raise SkipTest("DATABASE_URL_TEST not set")
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    test_pw = "TempP@ssw0rd"
    hashed_pw = pwd_context.hash(test_pw)

    engine = create_async_engine(DATABASE_URL, future=True)
    conn = await engine.connect()
    trans = await conn.begin()
    try:
        await conn.execute(
            text("INSERT INTO users(email, password) VALUES(:e, :p)"),
            {"e": test_email, "p": hashed_pw}
        )
        result = await conn.execute(
            text("SELECT password FROM users WHERE email = :e"),
            {"e": test_email}
        )
        row = await result.fetchone()
        assert row is not None, "inserted user not found"
        assert pwd_context.verify(test_pw, row[0]), "stored hash mismatch"
    finally:
        await trans.rollback()
        await conn.close()
        await engine.dispose()
    return True

async def test_blob_storage():
    logger.info("Running test: Azure Blob Storage")
    if need_skip(STORAGE_ACCOUNT_URL):
        raise SkipTest("AZURE_STORAGE_ACCOUNT_URL not set")
    credential = DefaultAzureCredential()
    blob_service = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)
    blob_name = f"test_blob_{uuid.uuid4().hex}.txt"
    client = blob_service.get_container_client(STORAGE_CONTAINER).get_blob_client(blob_name)
    data = b"Hello, Blob!"

    try:
        await client.upload_blob(data)
        downloaded = await client.download_blob()
        content = await downloaded.readall()
        assert content == data, "downloaded content mismatch"
        await client.delete_blob()
    finally:
        await credential.close()
    return True

async def test_openai_embedding():
    logger.info("Running test: Azure OpenAI embedding")
    if any(need_skip(v) for v in [OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_DEPLOYMENT_NAME]):
        raise SkipTest("OpenAI config not fully set")
    client = AsyncAzureOpenAI(
        deployment_name=OPENAI_DEPLOYMENT_NAME,
        api_type=OPENAI_API_TYPE,
        api_key=OPENAI_API_KEY,
        api_base=OPENAI_API_BASE,
        api_version=OPENAI_API_VERSION,
    )
    try:
        resp = await client.embeddings.create(input=["test"], model=OPENAI_DEPLOYMENT_NAME)
        assert resp.embeddings and len(resp.embeddings) == 1, "unexpected embedding response"
    finally:
        await client.aclose()
    return True

# --- Main Runner ---
async def main():
    tests = [
        test_password_hashing,
        test_database_connection,
        test_user_login_flow,
        test_blob_storage,
        test_openai_embedding,
    ]
    total = passed = skipped = failed = 0

    for test in tests:
        total += 1
        try:
            await test()
            logger.info(f"[PASS] {test.__name__}")
            passed += 1
        except SkipTest as e:
            logger.warning(f"[SKIP] {test.__name__} skipped: {e}")
            skipped += 1
        except AssertionError as e:
            logger.error(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1
        except Exception:
            logger.exception(f"[ERROR] {test.__name__} error")
            failed += 1

    logger.info("----- Summary -----")
    logger.info(f"Total: {total}, Passed: {passed}, Skipped: {skipped}, Failed: {failed}")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    asyncio.run(main())

