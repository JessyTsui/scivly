import asyncio
import os
from collections.abc import Callable, Generator

import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.config import get_settings

DEMO_WORKSPACE_ID = "00000000-0000-0000-0000-000000000201"
FREE_WORKSPACE_ID = "00000000-0000-0000-0000-000000009901"
FREE_USER_ID = "00000000-0000-0000-0000-000000009902"


def _run_sql(statement: str) -> None:
    async def _execute() -> None:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"])
        try:
            await connection.execute(statement)
        finally:
            await connection.close()

    asyncio.run(_execute())


def _fetchrow(statement: str) -> asyncpg.Record | None:
    async def _execute() -> asyncpg.Record | None:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"])
        try:
            return await connection.fetchrow(statement)
        finally:
            await connection.close()

    return asyncio.run(_execute())


@pytest.fixture()
def stripe_config(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("SCIVLY_STRIPE_SECRET_KEY", "sk_test_123")
    monkeypatch.setenv("SCIVLY_STRIPE_WEBHOOK_SECRET", "whsec_test_123")
    monkeypatch.setenv("SCIVLY_STRIPE_PRO_PRICE_ID", "price_pro_test_123")
    monkeypatch.setenv("SCIVLY_APP_URL", "http://localhost:3100")
    get_settings.cache_clear()

    try:
        yield
    finally:
        get_settings.cache_clear()


def test_billing_summary_reports_soft_limit_warnings(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
    stripe_config: None,
) -> None:
    headers = auth_headers(workspace_id=FREE_WORKSPACE_ID, local_user_id=FREE_USER_ID)

    bootstrap = client.get("/billing/subscription", headers=headers)
    assert bootstrap.status_code == 200
    assert bootstrap.json()["plan"] == "free"

    _run_sql(
        f"""
        INSERT INTO usage_records (
          workspace_id,
          record_type,
          quantity,
          unit_cost,
          metadata,
          recorded_at
        )
        VALUES (
          '{FREE_WORKSPACE_ID}',
          'paper_process',
          10,
          0,
          '{{"source":"test"}}'::jsonb,
          now()
        );
        """
    )

    response = client.get("/billing/subscription", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    papers_limit = next(item for item in payload["usage_limits"] if item["key"] == "papers_processed")
    assert papers_limit["limit"] == 10
    assert papers_limit["used"] == 10
    assert papers_limit["remaining"] == 0
    assert papers_limit["soft_limited"] is True
    assert payload["overage_warning"] is True

    usage_response = client.get("/usage", headers=headers)
    assert usage_response.status_code == 200
    assert usage_response.json()["overage_warning"] is True


def test_create_checkout_session_creates_customer_and_returns_url(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
    stripe_config: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_customer_create(**kwargs):
        captured["customer_kwargs"] = kwargs
        return {"id": "cus_checkout_test_123"}

    def fake_checkout_create(**kwargs):
        captured["checkout_kwargs"] = kwargs
        return {
            "id": "cs_test_checkout_123",
            "url": "https://checkout.stripe.com/c/pay/cs_test_checkout_123",
        }

    monkeypatch.setattr("app.routers.billing.stripe.Customer.create", fake_customer_create)
    monkeypatch.setattr("app.routers.billing.stripe.checkout.Session.create", fake_checkout_create)

    response = client.post(
        "/billing/checkout-session",
        json={"plan": "pro"},
        headers=auth_headers(workspace_id=FREE_WORKSPACE_ID, local_user_id=FREE_USER_ID),
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == "cs_test_checkout_123"
    assert payload["url"].startswith("https://checkout.stripe.com/")
    assert captured["customer_kwargs"] == {
        "email": "user_test@users.scivly.invalid",
        "name": "Researcher r_test Workspace",
        "metadata": {"workspace_id": FREE_WORKSPACE_ID},
    }
    checkout_kwargs = captured["checkout_kwargs"]
    assert isinstance(checkout_kwargs, dict)
    assert checkout_kwargs["line_items"] == [{"price": "price_pro_test_123", "quantity": 1}]
    assert checkout_kwargs["metadata"] == {"workspace_id": FREE_WORKSPACE_ID, "plan": "pro"}
    assert checkout_kwargs["subscription_data"] == {
        "metadata": {"workspace_id": FREE_WORKSPACE_ID, "plan": "pro"}
    }

    workspace_row = _fetchrow(
        f"""
        SELECT stripe_customer_id
        FROM workspaces
        WHERE id = '{FREE_WORKSPACE_ID}'
        """
    )
    assert workspace_row is not None
    assert workspace_row["stripe_customer_id"] == "cus_checkout_test_123"


def test_create_portal_session_returns_portal_url(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
    stripe_config: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client.get(
        "/billing/subscription",
        headers=auth_headers(workspace_id=FREE_WORKSPACE_ID, local_user_id=FREE_USER_ID),
    )
    _run_sql(
        f"""
        UPDATE workspaces
        SET stripe_customer_id = 'cus_portal_test_123'
        WHERE id = '{FREE_WORKSPACE_ID}';
        """
    )

    def fake_portal_create(**kwargs):
        assert kwargs["customer"] == "cus_portal_test_123"
        return {
            "id": "bps_test_123",
            "url": "https://billing.stripe.com/p/session/test_123",
        }

    monkeypatch.setattr("app.routers.billing.stripe.billing_portal.Session.create", fake_portal_create)

    response = client.post(
        "/billing/portal-session",
        json={},
        headers=auth_headers(workspace_id=FREE_WORKSPACE_ID, local_user_id=FREE_USER_ID),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": "bps_test_123",
        "url": "https://billing.stripe.com/p/session/test_123",
    }


def test_cancel_and_reactivate_subscription_updates_workspace(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
    stripe_config: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client.get(
        "/billing/subscription",
        headers=auth_headers(workspace_id=FREE_WORKSPACE_ID, local_user_id=FREE_USER_ID),
    )
    _run_sql(
        f"""
        UPDATE workspaces
        SET
          plan = 'pro',
          stripe_customer_id = 'cus_modify_test_123',
          stripe_subscription_id = 'sub_modify_test_123',
          stripe_price_id = 'price_pro_test_123',
          subscription_status = 'active',
          cancel_at_period_end = FALSE
        WHERE id = '{FREE_WORKSPACE_ID}';
        """
    )

    def fake_modify(subscription_id: str, **kwargs):
        return {
            "id": subscription_id,
            "customer": "cus_modify_test_123",
            "status": "active",
            "cancel_at_period_end": kwargs["cancel_at_period_end"],
            "current_period_end": 1_775_000_000,
            "items": {"data": [{"price": {"id": "price_pro_test_123"}}]},
            "metadata": {"workspace_id": FREE_WORKSPACE_ID, "plan": "pro"},
        }

    monkeypatch.setattr("app.routers.billing.stripe.Subscription.modify", fake_modify)

    cancel_response = client.post(
        "/billing/subscription/cancel",
        headers=auth_headers(workspace_id=FREE_WORKSPACE_ID, local_user_id=FREE_USER_ID),
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["cancel_at_period_end"] is True

    reactivate_response = client.post(
        "/billing/subscription/reactivate",
        headers=auth_headers(workspace_id=FREE_WORKSPACE_ID, local_user_id=FREE_USER_ID),
    )
    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["cancel_at_period_end"] is False


def test_stripe_webhook_updates_workspace_and_is_idempotent(
    client: TestClient,
    stripe_config: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event = {
        "id": "evt_test_subscription_updated",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_webhook_test_123",
                "customer": "cus_webhook_test_123",
                "status": "active",
                "cancel_at_period_end": False,
                "current_period_end": 1_776_000_000,
                "items": {"data": [{"price": {"id": "price_pro_test_123"}}]},
                "metadata": {"workspace_id": DEMO_WORKSPACE_ID, "plan": "pro"},
            }
        },
    }

    def fake_construct_event(payload: bytes, signature: str, secret: str):
        assert signature == "test-signature"
        assert secret == "whsec_test_123"
        return event

    monkeypatch.setattr("app.routers.billing.stripe.Webhook.construct_event", fake_construct_event)

    response = client.post(
        "/billing/webhooks/stripe",
        content=b"{}",
        headers={"stripe-signature": "test-signature"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Stripe event received."

    workspace_row = _fetchrow(
        f"""
        SELECT plan, stripe_customer_id, stripe_subscription_id, stripe_price_id, subscription_status
        FROM workspaces
        WHERE id = '{DEMO_WORKSPACE_ID}'
        """
    )
    assert workspace_row is not None
    assert workspace_row["plan"] == "pro"
    assert workspace_row["stripe_customer_id"] == "cus_webhook_test_123"
    assert workspace_row["stripe_subscription_id"] == "sub_webhook_test_123"
    assert workspace_row["stripe_price_id"] == "price_pro_test_123"
    assert workspace_row["subscription_status"] == "active"

    event_row = _fetchrow(
        """
        SELECT stripe_event_id, event_type
        FROM billing_events
        WHERE stripe_event_id = 'evt_test_subscription_updated'
        """
    )
    assert event_row is not None
    assert event_row["event_type"] == "customer.subscription.updated"

    second_response = client.post(
        "/billing/webhooks/stripe",
        content=b"{}",
        headers={"stripe-signature": "test-signature"},
    )
    assert second_response.status_code == 200
    assert second_response.json()["message"] == "Stripe event already processed."
