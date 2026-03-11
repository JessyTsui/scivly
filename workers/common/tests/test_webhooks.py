"""Webhook signing and retry tests."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import asyncio
import httpx

from workers.common.webhooks import (
    WEBHOOK_SIGNATURE_HEADER,
    WebhookDeliveryResult,
    WebhookEventEmitter,
    WebhookSubscription,
    serialize_webhook_payload,
    sign_webhook_payload,
    verify_webhook_signature,
)


class FakeWebhookRepository:
    def __init__(self) -> None:
        self.subscription = WebhookSubscription(
            id=uuid4(),
            workspace_id=uuid4(),
            url="https://hooks.example.com/retry",
            secret_hash="whsec_retry_secret",
        )
        self.created: list[dict[str, Any]] = []
        self.updates: list[dict[str, Any]] = []
        self.usages: list[dict[str, Any]] = []

    async def list_subscriptions(self, workspace_id: UUID, event_type: str) -> list[WebhookSubscription]:
        return [self.subscription] if workspace_id == self.subscription.workspace_id else []

    async def create_delivery(
        self,
        *,
        delivery_id,
        webhook_id,
        event_type,
        payload,
    ) -> None:
        self.created.append(
            {
                "delivery_id": delivery_id,
                "webhook_id": webhook_id,
                "event_type": event_type,
                "payload": payload,
            }
        )

    async def update_delivery(
        self,
        *,
        delivery_id,
        status,
        attempts,
        response_status_code,
        last_error,
        last_attempt_at,
        delivered_at,
    ) -> None:
        self.updates.append(
            {
                "delivery_id": delivery_id,
                "status": status,
                "attempts": attempts,
                "response_status_code": response_status_code,
                "last_error": last_error,
                "last_attempt_at": last_attempt_at,
                "delivered_at": delivered_at,
            }
        )

    async def record_usage(
        self,
        *,
        workspace_id,
        delivery_id,
        webhook_id,
        event_type,
        status,
    ) -> None:
        self.usages.append(
            {
                "workspace_id": workspace_id,
                "delivery_id": delivery_id,
                "webhook_id": webhook_id,
                "event_type": event_type,
                "status": status,
            }
        )

    async def aclose(self) -> None:
        return None


def test_sign_and_verify_webhook_signature() -> None:
    secret = "whsec_demo_secret"
    payload = serialize_webhook_payload({"event": "paper.matched", "score": 88})
    signature = sign_webhook_payload(secret, payload, timestamp=1_762_000_000)

    assert verify_webhook_signature(
        secret,
        payload,
        signature,
        tolerance_seconds=None,
    )
    assert not verify_webhook_signature(
        secret,
        serialize_webhook_payload({"event": "paper.matched", "score": 89}),
        signature,
        tolerance_seconds=None,
    )


def test_webhook_delivery_retries_until_success() -> None:
    repository = FakeWebhookRepository()
    sleeps: list[float] = []
    attempts = 0
    captured_headers: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        captured_headers.append(request.headers[WEBHOOK_SIGNATURE_HEADER])
        if attempts < 3:
            return httpx.Response(500, text=f"temporary failure {attempts}")
        return httpx.Response(202, json={"accepted": True})

    async def run_delivery() -> WebhookDeliveryResult:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            emitter = WebhookEventEmitter(
                repository=repository,
                http_client=http_client,
                backoff_base_seconds=1.0,
                sleep=_capture_sleep(sleeps),
            )
            try:
                results = await emitter.emit(
                    "paper.matched",
                    workspace_id=repository.subscription.workspace_id,
                    payload={"paper_id": str(uuid4()), "score": 91.2},
                    idempotency_key="match-step-001",
                )
            finally:
                await emitter.aclose()
            return results[0]

    result = asyncio.run(run_delivery())

    assert result.status == "sent"
    assert result.attempts == 3
    assert sleeps == [1.0, 2.0]
    assert len(repository.created) == 1
    assert [entry["status"] for entry in repository.updates] == ["retrying", "retrying", "sent"]
    assert [entry["attempts"] for entry in repository.updates] == [1, 2, 3]
    assert repository.usages and repository.usages[0]["status"] == "sent"
    assert len(captured_headers) == 3


def _capture_sleep(entries: list[float]):
    async def _sleep(duration: float) -> None:
        entries.append(duration)

    return _sleep
