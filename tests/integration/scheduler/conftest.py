"""Shared fixtures for scheduler integration tests."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.scheduler.main import app as scheduler_app


@pytest.fixture(autouse=True)
def mock_scheduler_for_tests():
    """Mock the global scheduler for integration tests so it appears running."""
    mock_sched = MagicMock()
    mock_sched.running = True

    # Return realistic job list for tests
    mock_job1 = MagicMock()
    mock_job1.id = "care_circle.daily_newsletter"
    mock_job1.name = "Daily Newsletter"
    mock_job1.next_run_time = None
    mock_job1.trigger = MagicMock()
    mock_job1.trigger.__str__.return_value = "cron[0 8 * * *]"

    mock_job2 = MagicMock()
    mock_job2.id = "care_circle.daily_session"
    mock_job2.name = "Daily Session Pregen"
    mock_job2.next_run_time = None
    mock_job2.trigger = MagicMock()
    mock_job2.trigger.__str__.return_value = "cron[0 6 * * *]"

    mock_job3 = MagicMock()
    mock_job3.id = "scheduler.cleanup_old_run_logs"
    mock_job3.name = "Cleanup Old Logs"
    mock_job3.next_run_time = None
    mock_job3.trigger = MagicMock()
    mock_job3.trigger.__str__.return_value = "cron[0 3 * * 0]"

    mock_sched.get_jobs.return_value = [mock_job1, mock_job2, mock_job3]

    with patch('app.scheduler.main.scheduler', mock_sched):
        with patch('app.scheduler.routers.health.scheduler', mock_sched):
            with patch('app.scheduler.routers.jobs.scheduler', mock_sched):
                yield mock_sched


@pytest.fixture(autouse=True)
def mock_db_for_cleanup():
    """Prevent real DB connections during cleanup task in tests."""
    from unittest.mock import AsyncMock, patch
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.rowcount = 5
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()

    with patch('app.db.database.async_session_local') as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        yield


@pytest.fixture
def scheduler_client():
    """TestClient for the scheduler server."""
    with TestClient(app=scheduler_app) as client:
        yield client
