"""Shared fixtures for scheduler unit tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_db_session():
    """Mock async DB session for scheduler tests."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def mock_scheduler():
    """Mock APScheduler instance."""
    scheduler = MagicMock()
    scheduler.running = True
    scheduler.get_jobs = MagicMock(return_value=[])
    scheduler.add_job = MagicMock()
    scheduler.pause_job = MagicMock()
    scheduler.resume_job = MagicMock()
    scheduler.reschedule_job = MagicMock()
    scheduler.shutdown = MagicMock()
    return scheduler
