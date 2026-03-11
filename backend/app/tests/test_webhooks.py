import asyncio
from collections.abc import Callable
from uuid import UUID

import httpx
from fastapi.testclient import TestClient

from workers.common.webhooks import (
    WEBHOOK_EVENT_HEADER,
    WEBHOOK_SIGNATURE_HEADER,
    WebhookEventEmitter,
    verify_webhook_signature,
)

TEST_WORKSPACE_ID = "00000000-0000-0000-0000-000000009901"


def test_create_update_delete_webhook(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    create_response = client.post(
        "/webhooks",
        json={
            "url": "https://hooks.example.com/scivly",
            "events": ["paper.matched", "digest.ready"],
        },
        headers=auth_headers(workspace_id=TEST_WORKSPACE_ID),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["secret_hash"].startswith("whsec_")
    assert created["secret_preview"].endswith(created["secret_hash"][-4:])
    assert created["events"] == ["paper.matched", "digest.ready"]

    list_response = client.get("/webhooks", headers=auth_headers(workspace_id=TEST_WORKSPACE_ID))
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    update_response = client.patch(
        f"/webhooks/{created['id']}",
        json={
            "events": ["paper.matched", "paper.enriched"],
            "is_active": False,
        },
        headers=auth_headers(workspace_id=TEST_WORKSPACE_ID),
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["events"] == ["paper.matched", "paper.enriched"]
    assert updated["is_active"] is False

    delete_response = client.delete(
        f"/webhooks/{created['id']}",
        headers=auth_headers(workspace_id=TEST_WORKSPACE_ID),
    )
    assert delete_response.status_code == 204

    final_response = client.get("/webhooks", headers=auth_headers(workspace_id=TEST_WORKSPACE_ID))
    assert final_response.status_code == 200
    assert final_response.json()["total"] == 0


def test_registered_webhook_receives_signed_match_event(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    create_response = client.post(
        "/webhooks",
        json={
            "url": "https://hooks.example.com/receiver",
            "events": ["paper.matched"],
        },
        headers=auth_headers(workspace_id=TEST_WORKSPACE_ID),
    )
    assert create_response.status_code == 201
    created = create_response.json()

    received_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        received_requests.append(request)
        return httpx.Response(202, json={"accepted": True})

    async def emit_event() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            emitter = WebhookEventEmitter(http_client=http_client)
            try:
                result = await emitter.emit(
                    "paper.matched",
                    workspace_id=UUID(TEST_WORKSPACE_ID),
                    payload={
                        "paper_id": "00000000-0000-0000-0000-000000001001",
                        "score": 87.5,
                        "matched_rules": ["topic:agents", "author:tracked"],
                    },
                    idempotency_key="match-task-001",
                )
            finally:
                await emitter.aclose()

            assert len(result) == 1
            assert result[0].status == "sent"
            assert result[0].attempts == 1

    asyncio.run(emit_event())

    assert len(received_requests) == 1
    request = received_requests[0]
    assert request.headers[WEBHOOK_EVENT_HEADER] == "paper.matched"
    assert request.headers["x-scivly-idempotency-key"] == "match-task-001"
    assert verify_webhook_signature(
        created["secret_hash"],
        request.content,
        request.headers[WEBHOOK_SIGNATURE_HEADER],
    )

    payload = client.get("/webhooks", headers=auth_headers(workspace_id=TEST_WORKSPACE_ID)).json()
    deliveries = payload["items"][0]["deliveries"]
    assert deliveries[0]["event_type"] == "paper.matched"
    assert deliveries[0]["last_status"] == "sent"
