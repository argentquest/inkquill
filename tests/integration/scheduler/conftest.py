"""Shared fixtures for scheduler integration tests."""

import pytest
from fastapi.testclient import TestClient
from app.scheduler.main import app as scheduler_app


@pytest.fixture
def scheduler_client():
    """TestClient for the scheduler server."""
    with TestClient(scheduler_app) as client:
        yield client
