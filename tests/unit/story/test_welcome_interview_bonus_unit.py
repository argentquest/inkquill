"""Mock-based unit tests for welcome interview bonus endpoints."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.routers.welcome_interview import router as welcome_interview_router


pytestmark = pytest.mark.unit


def test_bonus_status_endpoint_returns_wrapped_state(unit_client_factory):
    """`GET /ui/welcome-interview/api/bonus-status` should return wrapped bonus flags."""
    client = unit_client_factory(welcome_interview_router)

    response = client.get("/ui/welcome-interview/api/bonus-status")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["bonus1"] is False
    assert body["data"]["bonus10"] is False


def test_claim_bonus_already_claimed_returns_wrapped_payload(unit_client_factory, mock_user):
    """Claiming an already-claimed bonus should return wrapped `already_claimed=True`."""
    mock_user.bonus2 = True
    client = unit_client_factory(welcome_interview_router, user_override=mock_user)

    response = client.post(
        "/ui/welcome-interview/api/claim-bonus",
        json={"bonus_number": 2},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["already_claimed"] is True
    assert body["data"]["success"] is False


def test_claim_bonus_success_updates_account_and_returns_wrapped_payload(unit_client_factory, mock_user):
    """Claiming an unclaimed bonus should return wrapped success payload with awarded coins."""
    client = unit_client_factory(welcome_interview_router, user_override=mock_user)

    account = SimpleNamespace(
        id=50,
        current_balance=0,
        total_credits_added=0,
    )

    with patch("app.routers.welcome_interview.billing_crud.get_or_create_user_account", new=AsyncMock(return_value=account)), patch(
        "app.routers.welcome_interview.billing_crud.create_transaction", new=AsyncMock(return_value=SimpleNamespace(id=1))
    ):
        response = client.post(
            "/ui/welcome-interview/api/claim-bonus",
            json={"bonus_number": 2},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["success"] is True
    assert body["data"]["coins_awarded"] == 500
    assert body["data"]["already_claimed"] is False
