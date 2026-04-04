from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.ai_cost_log import AICallLog
from app.models.credit_package import CreditPackage
from app.models.referral import Referral, ReferralReward
from app.models.user import User
from app.models.user_account import UserAccount
from app.models.user_transaction import TransactionType, UserTransaction


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_billing_and_referral_endpoints_with_real_db_state(client, register_and_login, run_db):
    credentials, _ = register_and_login("billingflow")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    auth_headers = {"Authorization": f"Bearer {token}"}

    account_response = client.get("/api/v1/billing/account", headers=auth_headers)
    assert account_response.status_code == 200, account_response.text
    account_body = account_response.json()
    assert account_body["success"] is True
    assert Decimal(account_body["data"]["current_balance"]) == Decimal("2000.0000")

    def seed_billing_and_fetch_referrer_id(session):
        async def _inner():
            user = (
                await session.execute(select(User).where(User.username == credentials["username"]))
            ).scalar_one()
            package = CreditPackage(
                name="Integration Pack",
                description="Credits for integration tests",
                credit_amount=Decimal("500.0000"),
                price_usd=Decimal("4.99"),
                bonus_percentage=Decimal("10.00"),
                is_active=True,
                display_order=1,
            )
            session.add(package)
            await session.flush()

            ai_call = AICallLog(
                user_id=user.id,
                model_config_id=None,
                input_prompt="integration prompt",
                model_name="mock-billing-model",
                call_type="integration_test",
                object_id=None,
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                calculated_cost_usd=0.0125,
                duration_ms=42,
                created_at=datetime.now(timezone.utc),
            )
            session.add(ai_call)
            await session.commit()
            return {"user_id": user.id, "package_id": package.id}

        return _inner()

    seeded = run_db(seed_billing_and_fetch_referrer_id)
    referrer_id = seeded["user_id"]
    package_id = seeded["package_id"]

    balance_response = client.get("/api/v1/billing/balance", headers=auth_headers)
    assert balance_response.status_code == 200, balance_response.text
    assert balance_response.json()["success"] is True
    assert balance_response.json()["data"]["balance"] == 2000.0

    packages_response = client.get("/api/v1/billing/packages", headers=auth_headers)
    assert packages_response.status_code == 200, packages_response.text
    packages_body = packages_response.json()
    assert packages_body["success"] is True
    assert any(pkg["id"] == package_id for pkg in packages_body["data"])

    add_credits_response = client.post(
        "/api/v1/billing/add-credits",
        json={"credit_package_id": package_id, "payment_reference": "integration-payment-001"},
        headers=auth_headers,
    )
    assert add_credits_response.status_code == 200, add_credits_response.text
    add_credits_body = add_credits_response.json()
    assert add_credits_body["success"] is True
    assert add_credits_body["data"]["credits_added"] == 550.0
    assert add_credits_body["data"]["new_balance"] == 2550.0

    transactions_response = client.get("/api/v1/billing/transactions", headers=auth_headers)
    assert transactions_response.status_code == 200, transactions_response.text
    transactions_body = transactions_response.json()
    assert transactions_body["success"] is True
    assert len(transactions_body["data"]) >= 2

    dashboard_response = client.get("/api/v1/billing/dashboard", headers=auth_headers)
    assert dashboard_response.status_code == 200, dashboard_response.text
    dashboard_body = dashboard_response.json()
    assert dashboard_body["success"] is True
    assert dashboard_body["data"]["account"]["current_balance"] == "2550.0000"
    assert len(dashboard_body["data"]["available_packages"]) >= 1

    balance_check_response = client.get("/api/v1/billing/balance-check/100", headers=auth_headers)
    assert balance_check_response.status_code == 200, balance_check_response.text
    balance_check_body = balance_check_response.json()
    assert balance_check_body["success"] is True
    assert balance_check_body["data"]["sufficient_balance"] is True

    recent_ai_costs = client.get("/api/v1/billing/ai-costs/recent", headers=auth_headers)
    assert recent_ai_costs.status_code == 200, recent_ai_costs.text
    recent_body = recent_ai_costs.json()
    assert recent_body["success"] is True
    assert recent_body["data"]["total_calls_today"] >= 1
    assert recent_body["data"]["recent_calls"][0]["model_name"] == "mock-billing-model"

    last_ai_call = client.get("/api/v1/billing/ai-costs/last", headers=auth_headers)
    assert last_ai_call.status_code == 200, last_ai_call.text
    last_call_body = last_ai_call.json()
    assert last_call_body["success"] is True
    assert last_call_body["data"]["last_call"]["model_name"] == "mock-billing-model"
    assert last_call_body["data"]["last_call_cost_coins"] == 125

    client.cookies.clear()
    track_response = client.post(
        "/api/v1/referrals/track",
        json={
            "referral_code": str(referrer_id),
            "landing_page": "http://testserver/join",
            "source_platform": "direct",
            "source_content_type": "world",
            "source_content_id": "42",
        },
    )
    assert track_response.status_code == 200, track_response.text
    track_body = track_response.json()
    assert track_body["success"] is True
    assert track_body["data"]["success"] is True
    assert track_body["data"]["reward_given"] is True
    assert track_body["data"]["reward_amount"] == 5

    referral_stats = client.get("/api/v1/referrals/stats", headers=auth_headers)
    assert referral_stats.status_code == 200, referral_stats.text
    referral_stats_body = referral_stats.json()
    assert referral_stats_body["success"] is True
    assert referral_stats_body["data"]["total_referrals"] >= 1
    assert referral_stats_body["data"]["total_coins_earned"] >= 5

    referral_history = client.get("/api/v1/referrals/history", headers=auth_headers)
    assert referral_history.status_code == 200, referral_history.text
    referral_history_body = referral_history.json()
    assert referral_history_body["success"] is True
    assert referral_history_body["data"]["total"] >= 1
    assert referral_history_body["data"]["referrals"][0]["source_platform"] == "direct"

    referral_rewards = client.get("/api/v1/referrals/rewards", headers=auth_headers)
    assert referral_rewards.status_code == 200, referral_rewards.text
    referral_rewards_body = referral_rewards.json()
    assert referral_rewards_body["success"] is True
    assert referral_rewards_body["data"]["total"] >= 1
    assert referral_rewards_body["data"]["rewards"][0]["coin_amount"] == 5

    def fetch_billing_and_referral_state(session):
        async def _inner():
            account = (
                await session.execute(select(UserAccount).where(UserAccount.user_id == referrer_id))
            ).scalar_one()
            transactions = (
                await session.execute(
                    select(UserTransaction)
                    .where(UserTransaction.user_account_id == account.id)
                    .order_by(UserTransaction.id)
                )
            ).scalars().all()
            referrals = (
                await session.execute(select(Referral).where(Referral.referrer_user_id == referrer_id))
            ).scalars().all()
            rewards = (
                await session.execute(select(ReferralReward).where(ReferralReward.user_id == referrer_id))
            ).scalars().all()
            return {
                "balance": account.current_balance,
                "transaction_types": [tx.transaction_type for tx in transactions],
                "referral_count": len(referrals),
                "reward_count": len(rewards),
            }

        return _inner()

    state = run_db(fetch_billing_and_referral_state)
    assert state["balance"] == Decimal("2555.0000")
    assert TransactionType.CREDIT_ADD in state["transaction_types"]
    assert TransactionType.REFERRAL_BONUS in state["transaction_types"]
    assert state["referral_count"] >= 1
    assert state["reward_count"] >= 1


def test_admin_billing_endpoints_can_inspect_and_adjust_accounts(client, register_and_login, run_db):
    admin_credentials, _ = register_and_login("billingadmin")
    user_credentials, _ = register_and_login("billinguser")

    def promote_admin_and_seed_package(session):
        async def _inner():
            admin = (
                await session.execute(select(User).where(User.username == admin_credentials["username"]))
            ).scalar_one()
            user = (
                await session.execute(select(User).where(User.username == user_credentials["username"]))
            ).scalar_one()
            admin.is_admin = True
            package = CreditPackage(
                name="Admin Seed Pack",
                description="Package to ensure admin dashboard has billing data",
                credit_amount=Decimal("250.0000"),
                price_usd=Decimal("2.99"),
                bonus_percentage=Decimal("0.00"),
                is_active=True,
                display_order=2,
            )
            session.add(package)
            await session.commit()
            return {"user_id": user.id}

        return _inner()

    seeded = run_db(promote_admin_and_seed_package)
    target_user_id = seeded["user_id"]

    target_token = _get_access_token(client, user_credentials["username"], user_credentials["password"])
    target_headers = {"Authorization": f"Bearer {target_token}"}
    target_account = client.get("/api/v1/billing/account", headers=target_headers)
    assert target_account.status_code == 200, target_account.text

    admin_token = _get_access_token(client, admin_credentials["username"], admin_credentials["password"])
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    dashboard_response = client.get("/api/v1/admin/billing/dashboard", headers=admin_headers)
    assert dashboard_response.status_code == 200, dashboard_response.text
    dashboard_body = dashboard_response.json()
    assert dashboard_body["success"] is True
    assert dashboard_body["data"]["system_stats"]["total_users"] >= 2

    users_response = client.get("/api/v1/admin/billing/users", headers=admin_headers)
    assert users_response.status_code == 200, users_response.text
    users_body = users_response.json()
    assert users_body["success"] is True
    assert any(account["user_id"] == target_user_id for account in users_body["data"])

    adjustment_response = client.post(
        "/api/v1/admin/billing/adjust-credits",
        json={
            "user_id": target_user_id,
            "amount": "125.0000",
            "description": "Integration admin adjustment",
        },
        headers=admin_headers,
    )
    assert adjustment_response.status_code == 200, adjustment_response.text
    adjustment_body = adjustment_response.json()
    assert adjustment_body["success"] is True
    assert adjustment_body["data"]["transaction_id"]

    transactions_response = client.get("/api/v1/admin/billing/transactions", headers=admin_headers)
    assert transactions_response.status_code == 200, transactions_response.text
    transactions_body = transactions_response.json()
    assert transactions_body["success"] is True
    assert any(
        tx["description"].endswith("Integration admin adjustment") for tx in transactions_body["data"]
    )

    statistics_response = client.get("/api/v1/admin/billing/statistics", headers=admin_headers)
    assert statistics_response.status_code == 200, statistics_response.text
    statistics_body = statistics_response.json()
    assert statistics_body["success"] is True
    assert statistics_body["data"]["total_transactions"] >= 1

    def fetch_admin_adjustment_state(session):
        async def _inner():
            account = (
                await session.execute(select(UserAccount).where(UserAccount.user_id == target_user_id))
            ).scalar_one()
            transactions = (
                await session.execute(
                    select(UserTransaction)
                    .where(UserTransaction.user_account_id == account.id)
                    .order_by(UserTransaction.id)
                )
            ).scalars().all()
            return {
                "balance": account.current_balance,
                "has_admin_adjustment": any(
                    tx.transaction_type == TransactionType.ADMIN_ADJUSTMENT for tx in transactions
                ),
            }

        return _inner()

    state = run_db(fetch_admin_adjustment_state)
    assert state["balance"] == Decimal("2125.0000")
    assert state["has_admin_adjustment"] is True

def test_shared_conversation_cost_logging_records_ai_log_and_billing_transaction(client, register_and_login, run_db):
    credentials, _ = register_and_login("conversationcost")

    def seed_and_log_turn(session):
        async def _inner():
            from app.models.ai_model_config import AIModelConfiguration, AIModelTypeEnum, AIProviderEnum
            from app.models.user import User
            from app.models.user_account import UserAccount
            from app.models.user_transaction import UserTransaction, TransactionType
            from app.services.cost_tracker_service import log_conversation_turn

            user = (
                await session.execute(select(User).where(User.username == credentials["username"]))
            ).scalar_one()

            model = AIModelConfiguration(
                display_name="Conversation Cost Model",
                model_name="gpt-conversation-cost",
                description="Shared conversation billing coverage",
                provider=AIProviderEnum.OPENAI,
                model_type=AIModelTypeEnum.GENERATION,
                is_active=True,
                is_public_chat_default=False,
                max_tokens=4096,
                temperature=0.4,
                top_p=1.0,
                presence_penalty=0.0,
                frequency_penalty=0.0,
                is_json_mode=False,
                provider_cost_input_usd_pm=1.0,
                provider_cost_output_usd_pm=2.0,
                user_price_input_usd_pm=3.5,
                user_price_output_usd_pm=4.5,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)

            log_id = await log_conversation_turn(
                user_id=user.id,
                model_config=model,
                prompt_tokens=1200,
                completion_tokens=300,
                call_type="chatbot_turn",
                input_prompt="user: hello\nassistant:",
                duration_ms=275,
                db=session,
            )

            ai_log = (
                await session.execute(select(AICallLog).where(AICallLog.id == log_id))
            ).scalar_one()
            account = (
                await session.execute(select(UserAccount).where(UserAccount.user_id == user.id))
            ).scalar_one()
            transaction = (
                await session.execute(
                    select(UserTransaction)
                    .where(UserTransaction.ai_cost_log_id == log_id)
                    .where(UserTransaction.transaction_type == TransactionType.AI_COST_DEDUCTION)
                )
            ).scalar_one()

            return {
                "log_id": log_id,
                "prompt_tokens": ai_log.prompt_tokens,
                "completion_tokens": ai_log.completion_tokens,
                "total_tokens": ai_log.total_tokens,
                "cost_usd": str(ai_log.calculated_cost_usd),
                "account_balance": str(account.current_balance),
                "transaction_amount": str(transaction.amount),
                "transaction_balance_after": str(transaction.balance_after),
                "transaction_description": transaction.description,
                "transaction_metadata": transaction.transaction_metadata,
            }

        return _inner()

    state = run_db(seed_and_log_turn)
    assert state["prompt_tokens"] == 1200
    assert state["completion_tokens"] == 300
    assert state["total_tokens"] == 1500
    assert state["cost_usd"] == "0.00555000"
    assert state["account_balance"] == "1944.5000"
    assert state["transaction_amount"] == "-55.5000"
    assert state["transaction_balance_after"] == "1944.5000"
    assert "1200 input / 300 output / 1500 total tokens" in state["transaction_description"]
    assert state["transaction_metadata"]["call_type"] == "chatbot_turn"
    assert state["transaction_metadata"]["prompt_tokens"] == 1200
    assert state["transaction_metadata"]["completion_tokens"] == 300
    assert state["transaction_metadata"]["total_tokens"] == 1500
    assert state["transaction_metadata"]["cost_usd"] == "0.00555000"
    assert state["transaction_metadata"]["coins_charged"] == "55.5000"
