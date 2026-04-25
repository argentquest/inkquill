import asyncio
import re
import shutil
import sys
import tempfile
import types
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import asyncpg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


SOURCE_DB_NAME = "inkquill_codebase"
DB_USER = "inkquill"
DB_PASSWORD = "changeme"
DB_HOST = "localhost"
DB_PORT = 5432


def run_async(coro):
    return asyncio.run(coro)


def _validate_db_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", name):
        raise ValueError(f"Unsafe database name: {name}")
    return name


async def _admin_connection():
    return await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database="postgres",
        host=DB_HOST,
        port=DB_PORT,
    )


async def _drop_database_if_exists(db_name: str) -> None:
    db_name = _validate_db_name(db_name)
    conn = await _admin_connection()
    try:
        await _terminate_database_connections(conn, db_name)
        await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
    finally:
        await conn.close()


async def _terminate_database_connections(conn: asyncpg.Connection, db_name: str) -> None:
    await conn.execute(
        """
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = $1 AND pid <> pg_backend_pid()
        """,
        db_name,
    )


async def _clone_database(source_db: str, target_db: str) -> None:
    source_db = _validate_db_name(source_db)
    target_db = _validate_db_name(target_db)
    conn = await _admin_connection()
    try:
        await _terminate_database_connections(conn, source_db)
        await _terminate_database_connections(conn, target_db)
        await conn.execute(f'CREATE DATABASE "{target_db}" TEMPLATE "{source_db}"')
    finally:
        await conn.close()


class FakeEmailService:
    async def send_welcome_email(self, *args, **kwargs):
        return True

    async def send_password_reset_email(self, *args, **kwargs):
        return True

    async def send_story_completion_email(self, *args, **kwargs):
        return True

    async def send_care_circle_invite_email(self, *args, **kwargs):
        return True


@pytest.fixture(scope="session")
def integration_db_name():
    db_name = f"inkquill_test_{uuid4().hex[:12]}"
    run_async(_drop_database_if_exists(db_name))
    run_async(_clone_database(SOURCE_DB_NAME, db_name))
    yield db_name
    run_async(_drop_database_if_exists(db_name))


@pytest.fixture(scope="session")
def test_db_url(integration_db_name):
    return (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{integration_db_name}"
    )


@pytest.fixture(scope="session")
def integration_temp_root():
    root = Path(tempfile.mkdtemp(prefix="inbkandquill2-integration-"))
    yield root
    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture(scope="session")
def app_instance(test_db_url, integration_temp_root):
    from app.core import config as config_module

    config_module.settings.APP_ENV = "test"
    config_module.settings.LOCAL_STORAGE_BASE_PATH = str(integration_temp_root / "uploads")
    config_module.settings.LOCAL_STORAGE_PUBLISHED_STORIES_PATH = "published"
    config_module.settings.LOCAL_STORAGE_GENERATED_IMAGES_PATH = "generated_images"
    config_module.settings.LOCAL_STORAGE_DOCUMENTS_PATH = "documents"
    config_module.settings.LOCAL_STORAGE_BLOG_MEDIA_PATH = "blog_media"
    config_module.settings.BACKEND_CORS_ORIGINS = ["http://testserver"]
    config_module.settings.EMAIL_TEST_MODE = True
    config_module.settings.EMAIL_TEST_ADDRESS = "integration-tests@example.com"
    config_module.SQLALCHEMY_DATABASE_URI = test_db_url

    test_engine = create_async_engine(
        test_db_url,
        pool_pre_ping=True,
        echo=False,
        pool_size=5,
        max_overflow=5,
        pool_timeout=60,
        pool_recycle=1800,
    )
    test_session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    import app.db.database as db_module
    db_module.engine = test_engine
    db_module.async_session_local = test_session_factory

    import app.core.deps as deps_module
    deps_module.async_session_local = test_session_factory

    import app.core.middleware as middleware_module
    middleware_module.async_session_local = test_session_factory

    import app.services.ai_model_cache as ai_model_cache_module
    ai_model_cache_module.async_session_local = test_session_factory

    async def fake_load_models_from_db():
        cache = ai_model_cache_module.model_cache
        cache.configurations = {}
        cache.generation_models = {}
        cache.default_generation_model = None

    ai_model_cache_module.model_cache.load_models_from_db = fake_load_models_from_db

    import app.routers.auth as auth_router

    auth_router.EmailService = FakeEmailService

    async def fake_convert_anonymous_referral(*args, **kwargs):
        return True

    auth_router.referral_service.convert_anonymous_referral = fake_convert_anonymous_referral

    import app.routers.act as act_router

    async def fake_generate_ai_summary_for_act(*args, **kwargs):
        return "integration-summary"

    act_router.generate_ai_summary_for_act = fake_generate_ai_summary_for_act

    import app.routers.scene as scene_router

    async def fake_generate_ai_summary_for_scene(*args, **kwargs):
        return "integration-summary"

    scene_router.generate_ai_summary_for_scene = fake_generate_ai_summary_for_scene

    if "aiofiles" not in sys.modules:
        aiofiles_module = types.ModuleType("aiofiles")
        aiofiles_os_module = types.ModuleType("aiofiles.os")

        class _AsyncFile:
            def __init__(self, path, mode):
                self._path = path
                self._mode = mode
                self._fh = None

            async def __aenter__(self):
                self._fh = open(self._path, self._mode)
                return self

            async def __aexit__(self, exc_type, exc, tb):
                if self._fh:
                    self._fh.close()

            async def write(self, data):
                return self._fh.write(data)

            async def read(self):
                return self._fh.read()

        def _aiofiles_open(path, mode="r", *args, **kwargs):
            return _AsyncFile(path, mode)

        async def _aiofiles_remove(path):
            Path(path).unlink(missing_ok=True)

        aiofiles_module.open = _aiofiles_open
        aiofiles_os_module.remove = _aiofiles_remove
        aiofiles_module.os = aiofiles_os_module
        sys.modules["aiofiles"] = aiofiles_module
        sys.modules["aiofiles.os"] = aiofiles_os_module

    import app.main as app_main
    from app.db.database import Base
    from app.services.email_service import get_email_service

    async def ensure_all_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(
                text(
                    """
                    ALTER TABLE care_circle_patient_content_cards
                    ADD COLUMN IF NOT EXISTS rendered_html TEXT
                    """
                )
            )
            await conn.execute(
                text(
                    """
                    ALTER TABLE care_circle_family_memberships
                    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'active'
                    """
                )
            )
            await conn.execute(
                text(
                    """
                    ALTER TABLE care_circle_families
                    ADD COLUMN IF NOT EXISTS is_disabled BOOLEAN NOT NULL DEFAULT FALSE
                    """
                )
            )

    run_async(ensure_all_tables())

    app_main.engine = test_engine
    app_main.storytelling_runtime.kernel = SimpleNamespace(plugins={})
    app_main.storytelling_runtime.review_act_content_function = object()
    app_main.app.dependency_overrides[get_email_service] = lambda: FakeEmailService()
    app_main.app.state.test_session_factory = test_session_factory
    app_main.app.state.test_db_url = test_db_url
    app_main.app.state.test_storage_root = integration_temp_root

    yield app_main.app

    app_main.app.dependency_overrides.clear()
    run_async(test_engine.dispose())


@pytest.fixture
def client(app_instance):
    with TestClient(app_instance) as test_client:
        yield test_client


@pytest.fixture
def make_user_payload():
    def _make(prefix: str = "user"):
        suffix = uuid4().hex[:10]
        return {
            "username": f"{prefix}_{suffix}",
            "email": f"{prefix}_{suffix}@example.com",
            "password": "integration-pass-123",
            "display_name": f"{prefix.title()} {suffix}",
            "terms_accepted": True,
        }

    return _make


@pytest.fixture
def register_and_login(client):
    def _register_and_login(prefix: str = "user"):
        payload = {
            "username": f"{prefix}_{uuid4().hex[:10]}",
            "email": f"{prefix}_{uuid4().hex[:10]}@example.com",
            "password": "integration-pass-123",
            "display_name": f"{prefix.title()} Integration User",
            "terms_accepted": True,
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201, response.text
        return payload, response

    return _register_and_login


@pytest.fixture
def run_db(app_instance):
    test_db_url = app_instance.state.test_db_url

    def _run(fn):
        async def runner():
            engine = create_async_engine(
                test_db_url,
                poolclass=NullPool,
            )
            session_factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )
            try:
                async with session_factory() as session:
                    return await fn(session)
            finally:
                await engine.dispose()

        return asyncio.run(runner())

    return _run

