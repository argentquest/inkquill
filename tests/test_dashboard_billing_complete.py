# tests/test_dashboard_billing_complete.py

"""
Comprehensive tests for Dashboard and Billing API endpoints
Tests user analytics, subscription management, and payment processing with ApiResponse wrappers
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.routers import dashboard as dashboard_router
from app.routers import billing as billing_router


class TestDashboardEndpoints:
    """Test dashboard summary and analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /dashboard/summary - Get user dashboard summary successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.dashboard.crud_world') as mock_world_crud, \
             patch('app.routers.dashboard.crud_story') as mock_story_crud, \
             patch('app.routers.dashboard.crud_character') as mock_char_crud, \
             patch('app.routers.dashboard.crud_location') as mock_loc_crud, \
             patch('app.routers.dashboard.crud_lore_item') as mock_lore_crud:

            mock_get_user.return_value = mock_authenticated_user

            # Mock dashboard statistics
            mock_world_crud.count_worlds_by_user.return_value = 3
            mock_story_crud.count_stories_by_user.return_value = 12
            mock_char_crud.count_characters_by_user.return_value = 47
            mock_loc_crud.count_locations_by_user.return_value = 18
            mock_lore_crud.count_lore_items_by_user.return_value = 9

            client = test_client_factory.create_client_with_routers(dashboard_router.router)

            response = client.get("/dashboard/summary")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "data" in data
            dashboard = data["data"]
            assert dashboard["summary"]["total_worlds"] == 3
            assert dashboard["summary"]["total_stories"] == 12
            assert dashboard["summary"]["total_characters"] == 47
            assert dashboard["summary"]["total_locations"] == 18
            assert dashboard["summary"]["total_lore_items"] == 9

    @pytest.mark.asyncio
    async def test_get_dashboard_summary_empty_user(self, test_client_factory, mock_authenticated_user):
        """Test GET /dashboard/summary - New user with no content."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.dashboard.crud_world') as mock_world_crud, \
             patch('app.routers.dashboard.crud_story') as mock_story_crud, \
             patch('app.routers.dashboard.crud_character') as mock_char_crud, \
             patch('app.routers.dashboard.crud_location') as mock_loc_crud, \
             patch('app.routers.dashboard.crud_lore_item') as mock_lore_crud:

            mock_get_user.return_value = mock_authenticated_user

            # Mock empty counts (new user)
            mock_world_crud.count_worlds_by_user.return_value = 0
            mock_story_crud.count_stories_by_user.return_value = 0
            mock_char_crud.count_characters_by_user.return_value = 0
            mock_loc_crud.count_locations_by_user.return_value = 0
            mock_lore_crud.count_lore_items_by_user.return_value = 0

            client = test_client_factory.create_client_with_routers(dashboard_router.router)

            response = client.get("/dashboard/summary")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            dashboard = data["data"]
            assert dashboard["summary"]["total_worlds"] == 0
            assert dashboard["summary"]["total_stories"] == 0

    @pytest.mark.asyncio
    async def test_get_dashboard_recent_activity(self, test_client_factory, mock_authenticated_user):
        """Test GET /dashboard/recent-activity - Get recent user activity."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.dashboard.crud_story') as mock_story_crud, \
             patch('app.routers.dashboard.crud_character') as mock_char_crud:

            mock_get_user.return_value = mock_authenticated_user

            # Mock recent activity
            recent_stories = [
                Mock(title="Recent Story", created_at=datetime.utcnow()),
                Mock(title="Older Story", created_at=datetime.utcnow() - timedelta(hours=1))
            ]
            recent_characters = [
                Mock(name="New Character", created_at=datetime.utcnow())
            ]

            mock_story_crud.get_recent_stories_by_user.return_value = recent_stories
            mock_char_crud.get_recent_characters_by_user.return_value = recent_characters

            client = test_client_factory.create_client_with_routers(dashboard_router.router)

            response = client.get("/dashboard/recent-activity")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "recent_stories" in data["data"]
            assert "recent_characters" in data["data"]
            assert len(data["data"]["recent_stories"]) == 2
            assert len(data["data"]["recent_characters"]) == 1


class TestUserAccountEndpoints:
    """Test user account management and subscription-related endpoints."""

    @pytest.mark.asyncio
    async def test_get_account_status_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/account - Get user's account and billing status."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.billing_service') as mock_billing_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock account data
            account_data = {
                "user_id": mock_authenticated_user.id,
                "subscription_tier": "premium",
                "subscription_status": "active",
                "next_billing_date": "2024-12-01",
                "usage_this_month": {
                    "stories_created": 15,
                    "ai_tokens_used": 50000,
                    "characters_created": 25
                }
            }
            mock_billing_svc.get_account_summary.return_value = account_data

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/account")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            account = data["data"]
            assert account["subscription_tier"] == "premium"
            assert account["subscription_status"] == "active"

    @pytest.mark.asyncio
    async def test_get_account_balance_coins_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/balance - Get user coin balance."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.user_transaction_crud') as mock_transaction_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_get_db.return_value = AsyncMock()

            # Mock balance calculation - convert satoshis to coins (100000 sats = 1 coin)
            mock_balance = Mock()
            mock_balance.balance_satoshis = 2575000  # 25.75 coins
            mock_transaction_crud.get_user_balance.return_value = mock_balance

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/balance")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            balance_data = data["data"]
            assert balance_data["currency"] == "Coins"
            assert balance_data["balance"] == 25.75

    @pytest.mark.asyncio
    async def test_get_account_balance_zero_balance(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/balance - User with zero balance."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.user_transaction_crud') as mock_transaction_crud:

            mock_get_user.return_value = mock_authenticated_user
            mock_transaction_crud.get_user_balance.return_value = None  # No balance record

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/balance")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["balance"] == 0.0

    @pytest.mark.asyncio
    async def test_get_coin_balance_at_date(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/balance/{date} - Get balance at specific date."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.user_transaction_crud') as mock_transaction_crud:

            mock_get_user.return_value = mock_authenticated_user

            # Mock historical balance
            mock_historical_balance = Mock()
            mock_historical_balance.balance_satoshis = 1000000  # 10 coins
            mock_transaction_crud.get_user_balance_at_date.return_value = mock_historical_balance

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/balance/2024-01-15")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["balance"] == 10.0


class TestBillingPackageEndpoints:
    """Test billing package and pricing endpoints."""

    @pytest.mark.asyncio
    async def test_get_available_packages(self, test_client_factory):
        """Test GET /billing/packages - Get available billing packages."""
        with patch('app.routers.billing.credit_package_crud') as mock_package_crud:
            # Mock available packages
            mock_packages = [
                Mock(
                    id=1,
                    name="Starter Pack",
                    description="Perfect for new writers",
                    coin_amount=1000,
                    price_usd=9.99,
                    is_active=True
                ),
                Mock(
                    id=2,
                    name="Creator Pack",
                    description="For prolific writers",
                    coin_amount=2500,
                    price_usd=19.99,
                    is_active=True
                )
            ]
            mock_package_crud.get_active_packages.return_value = mock_packages

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/packages")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            packages = data["data"]
            assert len(packages) == 2
            assert packages[0]["name"] == "Starter Pack"
            assert packages[0]["coin_amount"] == 1000
            assert packages[1]["price_usd"] == 19.99

    @pytest.mark.asyncio
    async def test_purchase_coins_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /billing/purchase - Purchase coins successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.stripe_service') as mock_stripe_svc, \
             patch('app.routers.billing.billing_service') as mock_billing_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock Stripe payment intent
            mock_payment_intent = {
                "id": "pi_test123",
                "client_secret": "secret_test456",
                "status": "requires_payment_method"
            }
            mock_stripe_svc.create_payment_intent.return_value = mock_payment_intent

            client = test_client_factory.create_client_with_routers(billing_router.router)

            purchase_data = {
                "package_id": 1,
                "payment_method_id": "pm_test123"
            }

            response = client.post("/billing/purchase", json=purchase_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["client_secret"] == "secret_test456"
            assert data["data"]["payment_intent_id"] == "pi_test123"


class TestTransactionHistoryEndpoints:
    """Test transaction history and billing records."""

    @pytest.mark.asyncio
    async def test_get_transaction_history_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/transactions - Get user's transaction history."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.user_transaction_crud') as mock_transaction_crud:

            mock_get_user.return_value = mock_authenticated_user

            # Mock transaction history
            mock_transactions = [
                Mock(
                    id=1,
                    transaction_type="purchase",
                    amount_satoshis=1000000,  # 10 coins
                    description="Starter Pack Purchase",
                    created_at=datetime.utcnow()
                ),
                Mock(
                    id=2,
                    transaction_type="usage",
                    amount_satoshis=-50000,  # Used 0.5 coins
                    description="AI Story Generation",
                    created_at=datetime.utcnow() - timedelta(hours=1)
                )
            ]
            mock_transaction_crud.get_user_transactions.return_value = mock_transactions

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/transactions")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            transactions = data["data"]
            assert len(transactions) == 2

            # Check purchase transaction (positive amount)
            purchase_tx = transactions[0]
            assert purchase_tx["transaction_type"] == "purchase"
            assert purchase_tx["coin_amount"] == 10.0

            # Check usage transaction (negative amount)
            usage_tx = transactions[1]
            assert usage_tx["transaction_type"] == "usage"
            assert usage_tx["coin_amount"] == -0.5

    @pytest.mark.asyncio
    async def test_get_transaction_history_pagination(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/transactions - Pagination support."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.user_transaction_crud') as mock_transaction_crud:

            mock_get_user.return_value = mock_authenticated_user
            mock_transaction_crud.get_user_transactions.return_value = []

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/transactions?skip=10&limit=5")

            assert response.status_code == 200

            # Verify pagination parameters were passed
            mock_transaction_crud.get_user_transactions.assert_called_once()
            call_args = mock_transaction_crud.get_user_transactions.call_args
            assert call_args.kwargs["skip"] == 10
            assert call_args.kwargs["limit"] == 5


class TestAnalyticsEndpoints:
    """Test billing and usage analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_billing_dashboard_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/dashboard - Get comprehensive billing dashboard."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.billing_service') as mock_billing_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock comprehensive dashboard data
            dashboard_data = {
                "account_summary": {
                    "user_id": mock_authenticated_user.id,
                    "subscription_tier": "premium",
                    "balance_coins": 25.50
                },
                "usage_stats": {
                    "this_month": {
                        "stories_created": 12,
                        "characters_created": 28,
                        "ai_tokens_used": 45000
                    },
                    "last_month": {
                        "stories_created": 8,
                        "characters_created": 15,
                        "ai_tokens_used": 32000
                    }
                },
                "recent_transactions": [
                    {"type": "purchase", "amount": 10.0, "description": "Creator Pack"},
                    {"type": "usage", "amount": -2.5, "description": "Story Generation"}
                ],
                "cost_analysis": {
                    "by_feature": {
                        "story_generation": {"cost": 15.75, "usage": 45},
                        "character_creation": {"cost": 5.25, "usage": 15}
                    }
                }
            }
            mock_billing_svc.get_billing_dashboard.return_value = dashboard_data

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/dashboard")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            dashboard = data["data"]
            assert dashboard["account_summary"]["balance_coins"] == 25.50
            assert dashboard["usage_stats"]["this_month"]["stories_created"] == 12
            assert len(dashboard["recent_transactions"]) == 2

    @pytest.mark.asyncio
    async def test_get_last_ai_call_info(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/last-ai-call - Get info about last AI API call cost."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.cost_tracker_service') as mock_cost_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock last AI call information
            last_call_info = {
                "call_id": "call_123abc",
                "timestamp": datetime.utcnow(),
                "feature": "story_generation",
                "model": "gpt-4",
                "tokens_used": 1200,
                "cost_usd": 0.036,
                "cost_coins": float(0.036 * 1000000 / 100000),  # Convert USD to coins
                "call_type": "completion"
            }
            mock_cost_svc.get_user_last_ai_call.return_value = last_call_info

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/last-ai-call")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            call_info = data["data"]
            assert call_info["feature"] == "story_generation"
            assert call_info["model"] == "gpt-4"
            assert call_info["tokens_used"] == 1200

    @pytest.mark.asyncio
    async def test_get_recent_ai_costs(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/recent-ai-costs - Get recent AI usage costs."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.cost_tracker_service') as mock_cost_svc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock recent AI costs
            recent_costs = [
                {
                    "date": "2024-01-15",
                    "cost_usd": 2.45,
                    "cost_coins": 24.5,
                    "calls": 12,
                    "tokens": 45600
                },
                {
                    "date": "2024-01-14",
                    "cost_usd": 1.89,
                    "cost_coins": 18.9,
                    "calls": 8,
                    "tokens": 32900
                }
            ]
            mock_cost_svc.get_user_recent_ai_costs.return_value = recent_costs

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/recent-ai-costs?days=7")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            costs = data["data"]
            assert len(costs) == 2
            assert costs[0]["date"] == "2024-01-15"
            assert costs[0]["cost_coins"] == 24.5


class TestBillingErrorHandling:
    """Test error handling in billing endpoints."""

    @pytest.mark.asyncio
    async def test_purchase_insufficient_funds(self, test_client_factory, mock_authenticated_user):
        """Test POST /billing/purchase - Insufficient funds error."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.billing_service') as mock_billing_svc:

            mock_get_user.return_value = mock_authenticated_user
            mock_billing_svc.purchase_coins_with_stripe.side_effect = ValueError("Insufficient funds")

            client = test_client_factory.create_client_with_routers(billing_router.router)

            purchase_data = {
                "package_id": 999,  # Non-existent package
                "payment_method_id": "pm_test123"
            }

            response = client.post("/billing/purchase", json=purchase_data)

            # Should return 400 for validation/payment errors
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_balance_service_error(self, test_client_factory, mock_authenticated_user):
        """Test GET /billing/balance - Service error handling."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.billing.user_transaction_crud') as mock_transaction_crud:

            mock_get_user.return_value = mock_authenticated_user
            mock_transaction_crud.get_user_balance.side_effect = Exception("Database connection failed")

            client = test_client_factory.create_client_with_routers(billing_router.router)

            response = client.get("/billing/balance")

            assert response.status_code == 200  # Returns success with 0 balance for errors
            data = response.json()
            assert data["success"] is True
            assert data["data"]["balance"] == 0.0
            assert data["data"]["error"] is not None