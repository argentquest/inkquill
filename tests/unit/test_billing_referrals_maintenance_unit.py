"""Mock-based unit tests for billing, referrals, and maintenance routers."""

from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.models.user_transaction import TransactionType
from app.routers.billing import router as billing_router
from app.routers.maintenance import router as maintenance_router
from app.routers.referrals import router as referrals_router


pytestmark = pytest.mark.unit


def _account(user_id: int = 1):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=10,
        user_id=user_id,
        current_balance=Decimal("123.45"),
        total_spent=Decimal("10.00"),
        total_credits_added=Decimal("133.45"),
        currency="Coins",
        created_at=now,
        updated_at=now,
        user=SimpleNamespace(id=user_id, username="unit_user", email="unit@example.com", display_name="Unit User"),
    )


def _transaction():
    return SimpleNamespace(
        id=99,
        user_account_id=10,
        transaction_type=TransactionType.CREDIT_ADD,
        amount=Decimal("25.00"),
        balance_after=Decimal("123.45"),
        description="Unit top-up",
        created_at=datetime.now(timezone.utc),
        user_account=None,
    )


def _package():
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=3,
        name="Starter",
        description="Starter pack",
        credit_amount=Decimal("100.00"),
        price_usd=Decimal("9.99"),
        bonus_percentage=Decimal("0.00"),
        display_order=1,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def test_billing_account_dashboard_and_balance_check_are_wrapped(unit_client_factory):
    """Billing account/dashboard/balance-check endpoints return wrapped payloads."""
    client = unit_client_factory(billing_router, router_prefix="/api/v1")
    account = _account()
    tx = _transaction()
    pkg = _package()

    with patch("app.routers.billing.billing_crud.get_or_create_user_account", new=AsyncMock(return_value=account)), patch(
        "app.routers.billing.billing_crud.get_user_transactions", new=AsyncMock(return_value=[tx])
    ), patch("app.routers.billing.billing_crud.get_active_credit_packages", new=AsyncMock(return_value=[pkg])), patch(
        "app.routers.billing.billing_service.check_sufficient_balance", new=AsyncMock(return_value=True)
    ):
        account_response = client.get("/api/v1/billing/account")
        dashboard_response = client.get("/api/v1/billing/dashboard")
        balance_check_response = client.get("/api/v1/billing/balance-check/10.5")

    assert account_response.status_code == 200, account_response.text
    assert account_response.json()["success"] is True
    assert account_response.json()["data"]["current_balance"] == "123.45"

    assert dashboard_response.status_code == 200, dashboard_response.text
    dashboard_data = dashboard_response.json()["data"]
    assert dashboard_data["account"]["id"] == 10
    assert dashboard_data["recent_transactions"][0]["id"] == 99
    assert dashboard_data["available_packages"][0]["name"] == "Starter"

    assert balance_check_response.status_code == 200, balance_check_response.text
    assert balance_check_response.json()["data"]["sufficient_balance"] is True


def test_billing_balance_transactions_packages_and_add_credits(unit_client_factory):
    """Balance, transactions, packages, and add-credits endpoints return expected payloads."""
    client = unit_client_factory(billing_router, router_prefix="/api/v1")
    account = _account()
    tx = _transaction()
    pkg = _package()

    with patch("app.routers.billing.billing_service.get_user_balance", new=AsyncMock(return_value=Decimal("321.99"))), patch(
        "app.routers.billing.billing_crud.get_or_create_user_account", new=AsyncMock(return_value=account)
    ), patch("app.routers.billing.billing_crud.get_user_transactions", new=AsyncMock(return_value=[tx])), patch(
        "app.routers.billing.billing_crud.get_active_credit_packages", new=AsyncMock(return_value=[pkg])
    ), patch(
        "app.routers.billing.billing_service.add_credits",
        new=AsyncMock(return_value={"success": True, "new_balance": "148.45"}),
    ):
        balance_response = client.get("/api/v1/billing/balance")
        tx_response = client.get("/api/v1/billing/transactions")
        packages_response = client.get("/api/v1/billing/packages")
        add_response = client.post(
            "/api/v1/billing/add-credits",
            json={"credit_package_id": 3, "payment_reference": "pay_abc"},
        )

    assert balance_response.status_code == 200, balance_response.text
    assert balance_response.json()["data"]["balance"] == 321.99

    assert tx_response.status_code == 200, tx_response.text
    assert tx_response.json()["data"][0]["id"] == 99

    assert packages_response.status_code == 200, packages_response.text
    assert packages_response.json()["data"][0]["credit_amount"] == "100.00"

    assert add_response.status_code == 200, add_response.text
    assert add_response.json()["data"]["new_balance"] == "148.45"


def test_billing_recent_and_last_ai_cost_endpoints(unit_client_factory):
    """AI cost endpoints produce wrapped summaries with mocked cost-log data."""
    client = unit_client_factory(billing_router, router_prefix="/api/v1")
    now = datetime.now(timezone.utc)
    call = SimpleNamespace(
        id=7,
        model_name="gpt-unit",
        call_type="story_generation",
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30,
        calculated_cost_usd=0.0125,
        created_at=now,
        duration_ms=111,
    )

    with patch("app.routers.billing.crud_ai_cost.get_recent_ai_calls", new=AsyncMock(side_effect=[[call, call], [call]])), patch(
        "app.routers.billing.crud_ai_cost.get_daily_ai_cost_summary",
        new=AsyncMock(return_value=(2, 0.02, 60)),
    ):
        recent_response = client.get("/api/v1/billing/ai-costs/recent")
        last_response = client.get("/api/v1/billing/ai-costs/last")

    assert recent_response.status_code == 200, recent_response.text
    recent_data = recent_response.json()["data"]
    assert recent_data["total_calls_today"] == 2
    assert recent_data["recent_calls"][0]["id"] == 7

    assert last_response.status_code == 200, last_response.text
    last_data = last_response.json()["data"]
    assert last_data["last_call"]["model_name"] == "gpt-unit"
    assert last_data["last_call_cost_coins"] == 125
    assert last_data["total_cost_coins_today"] == 200


def test_referrals_stats_history_rewards_and_track(unit_client_factory, mock_db_session):
    """Referral endpoints return wrapped stats/history/rewards and track flow payloads."""
    client = unit_client_factory(referrals_router, router_prefix="/api/v1")

    referral_row = SimpleNamespace(
        id=1,
        referred_user_id=2,
        source_platform="x",
        source_content_type="story",
        is_converted=True,
        converted_at=datetime.now(timezone.utc),
        has_created_story=True,
        has_published_story=False,
        created_at=datetime.now(timezone.utc),
    )
    reward_row = SimpleNamespace(
        id=12,
        referral_id=1,
        reward_type="signup",
        coin_amount=50,
        awarded_at=datetime.now(timezone.utc),
    )
    tracked_referral = SimpleNamespace(id=1)

    history_result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [referral_row]))
    rewards_result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [reward_row]))
    latest_reward_result = SimpleNamespace(scalars=lambda: SimpleNamespace(first=lambda: reward_row))
    mock_db_session.execute = AsyncMock(side_effect=[history_result, rewards_result, latest_reward_result])

    with patch(
        "app.routers.referrals.referral_service.get_user_referral_stats",
        new=AsyncMock(
            return_value={
                "total_referrals": 3,
                "converted_referrals": 1,
                "conversion_rate": 33.3,
                "total_coins_earned": 50,
                "today": {"visits": 1},
                "platform_breakdown": {"x": 1},
                "limits": {"daily": 10},
                "reward_amounts": {"signup": 50},
            }
        ),
    ), patch("app.routers.referrals.referral_service.track_referral_visit", new=AsyncMock(return_value=tracked_referral)):
        stats_response = client.get("/api/v1/referrals/stats")
        history_response = client.get("/api/v1/referrals/history")
        rewards_response = client.get("/api/v1/referrals/rewards")
        track_response = client.post(
            "/api/v1/referrals/track",
            json={"referral_code": "5", "source_platform": "x", "landing_page": "https://example.com"},
        )

    assert stats_response.status_code == 200, stats_response.text
    assert stats_response.json()["data"]["total_referrals"] == 3

    assert history_response.status_code == 200, history_response.text
    assert history_response.json()["data"]["referrals"][0]["id"] == 1

    assert rewards_response.status_code == 200, rewards_response.text
    assert rewards_response.json()["data"]["rewards"][0]["coin_amount"] == 50

    assert track_response.status_code == 200, track_response.text
    track_data = track_response.json()["data"]
    assert track_data["success"] is True
    assert track_data["reward_given"] is True
    assert track_data["referral_id"] == 1


def test_maintenance_status_enable_disable(unit_client_factory, mock_admin_user):
    """Maintenance endpoints return wrapped status and enforce admin mode changes."""
    client = unit_client_factory(maintenance_router, router_prefix="/api/v1", user_override=mock_admin_user)

    with patch(
        "app.routers.maintenance.MaintenanceManager.get_maintenance_status",
        return_value={"enabled": True, "message": "Maint", "estimated_end_time": "soon"},
    ), patch("app.routers.maintenance.MaintenanceManager.set_maintenance_mode") as set_mode_mock:
        status_response = client.get("/api/v1/maintenance/status")
        enable_response = client.post("/api/v1/maintenance/enable?message=Upgrade&duration_minutes=10")
        disable_response = client.post("/api/v1/maintenance/disable")

    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["data"]["enabled"] is True

    assert enable_response.status_code == 200, enable_response.text
    assert enable_response.json()["data"]["status"] == "Maintenance mode enabled"
    set_mode_mock.assert_any_call(enabled=True, message="Upgrade", duration_minutes=10)

    assert disable_response.status_code == 200, disable_response.text
    assert disable_response.json()["data"]["status"] == "Maintenance mode disabled"
    set_mode_mock.assert_any_call(enabled=False)

