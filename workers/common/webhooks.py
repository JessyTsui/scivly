"""Webhook signing, delivery, and pipeline event dispatch helpers."""

from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Mapping, Protocol
from uuid import UUID, uuid4

import asyncpg
import httpx

from .task import TaskPayload

SUPPORTED_WEBHOOK_EVENTS: tuple[str, ...] = (
    "paper.matched",
    "paper.enriched",
    "digest.ready",
    "digest.delivered",
)
WEBHOOK_SIGNATURE_HEADER = "X-Scivly-Signature"
WEBHOOK_DELIVERY_HEADER = "X-Scivly-Delivery"
WEBHOOK_EVENT_HEADER = "X-Scivly-Event"
WEBHOOK_IDEMPOTENCY_HEADER = "X-Scivly-Idempotency-Key"
DEFAULT_DATABASE_URL = "postgresql://localhost:5432/scivly"


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def generate_webhook_secret() -> str:
    return f"whsec_{secrets.token_urlsafe(24)}"


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if database_url.startswith("postgres+asyncpg://"):
        return database_url.replace("postgres+asyncpg://", "postgres://", 1)
    return database_url


def _json_safe(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump(mode="json"))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return value


def serialize_webhook_payload(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        _json_safe(dict(payload)),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sign_webhook_payload(secret: str, payload: bytes, *, timestamp: int | None = None) -> str:
    issued_at = timestamp if timestamp is not None else int(utc_now().timestamp())
    signed_message = str(issued_at).encode("utf-8") + b"." + payload
    digest = hmac.new(secret.encode("utf-8"), signed_message, hashlib.sha256).hexdigest()
    return f"t={issued_at},v1={digest}"


def verify_webhook_signature(
    secret: str,
    payload: bytes | str,
    signature_header: str,
    *,
    tolerance_seconds: int | None = 300,
    now: dt.datetime | None = None,
) -> bool:
    timestamp: int | None = None
    received_signature: str | None = None

    for part in signature_header.split(","):
        key, _, value = part.partition("=")
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError:
                return False
        if key == "v1":
            received_signature = value

    if timestamp is None or not received_signature:
        return False

    body = payload.encode("utf-8") if isinstance(payload, str) else payload
    expected_signature = sign_webhook_payload(secret, body, timestamp=timestamp)
    expected_value = expected_signature.split("v1=", 1)[1]
    if not hmac.compare_digest(expected_value, received_signature):
        return False

    if tolerance_seconds is None:
        return True

    current_time = now or utc_now()
    issued_at = dt.datetime.fromtimestamp(timestamp, tz=dt.UTC)
    return abs((current_time - issued_at).total_seconds()) <= tolerance_seconds


@dataclass(frozen=True)
class WebhookSubscription:
    id: UUID
    workspace_id: UUID
    url: str
    secret_hash: str


@dataclass(frozen=True)
class WebhookDeliveryResult:
    delivery_id: UUID
    webhook_id: UUID
    event_type: str
    status: str
    attempts: int
    response_status_code: int | None = None
    last_error: str | None = None


class WebhookRepository(Protocol):
    async def list_subscriptions(self, workspace_id: UUID, event_type: str) -> list[WebhookSubscription]: ...

    async def create_delivery(
        self,
        *,
        delivery_id: UUID,
        webhook_id: UUID,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> None: ...

    async def update_delivery(
        self,
        *,
        delivery_id: UUID,
        status: str,
        attempts: int,
        response_status_code: int | None,
        last_error: str | None,
        last_attempt_at: dt.datetime,
        delivered_at: dt.datetime | None,
    ) -> None: ...

    async def record_usage(
        self,
        *,
        workspace_id: UUID,
        delivery_id: UUID,
        webhook_id: UUID,
        event_type: str,
        status: str,
    ) -> None: ...

    async def aclose(self) -> None: ...


class AsyncpgWebhookRepository:
    """Persist webhook subscriptions and delivery logs in Postgres."""

    def __init__(self, *, database_url: str | None = None) -> None:
        self.database_url = normalize_database_url(
            database_url or os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL
        )
        self._connection: asyncpg.Connection | None = None

    async def _get_connection(self) -> asyncpg.Connection:
        if self._connection is None:
            self._connection = await asyncpg.connect(self.database_url)
        return self._connection

    async def list_subscriptions(self, workspace_id: UUID, event_type: str) -> list[WebhookSubscription]:
        connection = await self._get_connection()
        rows = await connection.fetch(
            """
            SELECT id, workspace_id, url, secret_hash
            FROM webhooks
            WHERE workspace_id = $1
              AND is_active = TRUE
              AND $2 = ANY(events)
            ORDER BY created_at DESC
            """,
            workspace_id,
            event_type,
        )
        return [
            WebhookSubscription(
                id=row["id"],
                workspace_id=row["workspace_id"],
                url=row["url"],
                secret_hash=row["secret_hash"],
            )
            for row in rows
        ]

    async def create_delivery(
        self,
        *,
        delivery_id: UUID,
        webhook_id: UUID,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> None:
        connection = await self._get_connection()
        await connection.execute(
            """
            INSERT INTO webhook_deliveries (id, webhook_id, event_type, payload, status, attempts)
            VALUES ($1, $2, $3, $4::jsonb, 'queued', 0)
            """,
            delivery_id,
            webhook_id,
            event_type,
            json.dumps(_json_safe(dict(payload))),
        )

    async def update_delivery(
        self,
        *,
        delivery_id: UUID,
        status: str,
        attempts: int,
        response_status_code: int | None,
        last_error: str | None,
        last_attempt_at: dt.datetime,
        delivered_at: dt.datetime | None,
    ) -> None:
        connection = await self._get_connection()
        await connection.execute(
            """
            UPDATE webhook_deliveries
            SET status = $2,
                attempts = $3,
                response_status_code = $4,
                last_error = $5,
                last_attempt_at = $6,
                delivered_at = $7
            WHERE id = $1
            """,
            delivery_id,
            status,
            attempts,
            response_status_code,
            last_error,
            last_attempt_at,
            delivered_at,
        )

    async def record_usage(
        self,
        *,
        workspace_id: UUID,
        delivery_id: UUID,
        webhook_id: UUID,
        event_type: str,
        status: str,
    ) -> None:
        connection = await self._get_connection()
        await connection.execute(
            """
            INSERT INTO usage_records (workspace_id, record_type, quantity, unit_cost, metadata)
            VALUES ($1, 'delivery', 1, 0, $2::jsonb)
            """,
            workspace_id,
            json.dumps(
                {
                    "delivery_id": str(delivery_id),
                    "webhook_id": str(webhook_id),
                    "event_type": event_type,
                    "status": status,
                }
            ),
        )

    async def aclose(self) -> None:
        if self._connection is not None:
            await self._connection.close()
        self._connection = None


SleepFn = Callable[[float], Awaitable[None]]


class WebhookEventEmitter:
    """Deliver structured events to registered workspace webhooks."""

    def __init__(
        self,
        *,
        repository: WebhookRepository | None = None,
        http_client: httpx.AsyncClient | None = None,
        max_attempts: int = 3,
        backoff_base_seconds: float = 1.0,
        timeout_seconds: float = 10.0,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        self.repository = repository or AsyncpgWebhookRepository()
        self.http_client = http_client or httpx.AsyncClient(timeout=timeout_seconds)
        self.max_attempts = max_attempts
        self.backoff_base_seconds = backoff_base_seconds
        self.sleep = sleep
        self._owns_repository = repository is None
        self._owns_http_client = http_client is None

    async def emit(
        self,
        event_type: str,
        *,
        workspace_id: UUID,
        payload: Mapping[str, Any],
        idempotency_key: str | None = None,
    ) -> list[WebhookDeliveryResult]:
        if event_type not in SUPPORTED_WEBHOOK_EVENTS:
            raise ValueError(f"Unsupported webhook event: {event_type}")

        subscriptions = await self.repository.list_subscriptions(workspace_id, event_type)
        results: list[WebhookDeliveryResult] = []
        if not subscriptions:
            return results

        occurred_at = utc_now().isoformat()
        safe_payload = _json_safe(dict(payload))
        for subscription in subscriptions:
            delivery_id = uuid4()
            event_payload = {
                "id": str(delivery_id),
                "event": event_type,
                "workspace_id": str(workspace_id),
                "occurred_at": occurred_at,
                "data": safe_payload,
            }
            await self.repository.create_delivery(
                delivery_id=delivery_id,
                webhook_id=subscription.id,
                event_type=event_type,
                payload=event_payload,
            )
            results.append(
                await self._deliver_to_subscription(
                    subscription=subscription,
                    delivery_id=delivery_id,
                    event_type=event_type,
                    payload=event_payload,
                    idempotency_key=idempotency_key,
                )
            )
        return results

    async def _deliver_to_subscription(
        self,
        *,
        subscription: WebhookSubscription,
        delivery_id: UUID,
        event_type: str,
        payload: Mapping[str, Any],
        idempotency_key: str | None,
    ) -> WebhookDeliveryResult:
        serialized_payload = serialize_webhook_payload(payload)
        last_error: str | None = None
        response_status_code: int | None = None

        for attempt in range(1, self.max_attempts + 1):
            signature = sign_webhook_payload(subscription.secret_hash, serialized_payload)
            attempted_at = utc_now()
            response_status_code = None

            try:
                response = await self.http_client.post(
                    subscription.url,
                    content=serialized_payload,
                    headers={
                        "Content-Type": "application/json",
                        WEBHOOK_EVENT_HEADER: event_type,
                        WEBHOOK_DELIVERY_HEADER: str(delivery_id),
                        WEBHOOK_SIGNATURE_HEADER: signature,
                        WEBHOOK_IDEMPOTENCY_HEADER: idempotency_key or str(delivery_id),
                    },
                )
                response_status_code = response.status_code
                if 200 <= response.status_code < 300:
                    await self.repository.update_delivery(
                        delivery_id=delivery_id,
                        status="sent",
                        attempts=attempt,
                        response_status_code=response.status_code,
                        last_error=None,
                        last_attempt_at=attempted_at,
                        delivered_at=attempted_at,
                    )
                    await self.repository.record_usage(
                        workspace_id=subscription.workspace_id,
                        delivery_id=delivery_id,
                        webhook_id=subscription.id,
                        event_type=event_type,
                        status="sent",
                    )
                    return WebhookDeliveryResult(
                        delivery_id=delivery_id,
                        webhook_id=subscription.id,
                        event_type=event_type,
                        status="sent",
                        attempts=attempt,
                        response_status_code=response.status_code,
                    )

                last_error = self._build_http_error(response)
            except httpx.HTTPError as exc:
                last_error = str(exc)

            status = "retrying" if attempt < self.max_attempts else "failed"
            await self.repository.update_delivery(
                delivery_id=delivery_id,
                status=status,
                attempts=attempt,
                response_status_code=response_status_code,
                last_error=last_error,
                last_attempt_at=attempted_at,
                delivered_at=None,
            )
            if attempt < self.max_attempts:
                await self.sleep(self.backoff_base_seconds * (2 ** (attempt - 1)))

        return WebhookDeliveryResult(
            delivery_id=delivery_id,
            webhook_id=subscription.id,
            event_type=event_type,
            status="failed",
            attempts=self.max_attempts,
            response_status_code=response_status_code,
            last_error=last_error,
        )

    def _build_http_error(self, response: httpx.Response) -> str:
        body = response.text.strip()
        if len(body) > 200:
            body = body[:197] + "..."
        return f"HTTP {response.status_code}: {body or 'empty response body'}"

    async def aclose(self) -> None:
        if self._owns_http_client:
            await self.http_client.aclose()
        if self._owns_repository:
            await self.repository.aclose()


class PipelineWebhookEventEmitter:
    """Translate pipeline step events into webhook deliveries."""

    def __init__(self, *, dispatcher: WebhookEventEmitter | None = None) -> None:
        self.dispatcher = dispatcher or WebhookEventEmitter()

    async def emit(
        self,
        *,
        event_type: str,
        task: TaskPayload,
        payload: Mapping[str, Any],
    ) -> None:
        await self.dispatcher.emit(
            event_type,
            workspace_id=task.workspace_id,
            payload=payload,
            idempotency_key=task.idempotency_key,
        )

    async def aclose(self) -> None:
        await self.dispatcher.aclose()
