"""Integration tests for scheduler health endpoints."""

import pytest

pytestmark = pytest.mark.integration


def test_scheduler_health_returns_healthy(scheduler_client):
    """GET /scheduler/health returns healthy status."""
    response = scheduler_client.get("/scheduler/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["scheduler_running"] is True


def test_scheduler_status_lists_tasks(scheduler_client):
    """GET /scheduler/status lists all registered tasks."""
    response = scheduler_client.get("/scheduler/status")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    # At least the newsletter, session, and cleanup tasks should be registered
    assert len(tasks) >= 3
    task_keys = {t["key"] for t in tasks}
    assert "care_circle.daily_newsletter" in task_keys
    assert "care_circle.daily_session" in task_keys
    assert "scheduler.cleanup_old_run_logs" in task_keys
