from __future__ import annotations

import secrets
from typing import Sequence

SUPPORTED_WEBHOOK_EVENTS: tuple[str, ...] = (
    "paper.matched",
    "paper.enriched",
    "digest.ready",
    "digest.delivered",
)


def generate_webhook_secret() -> str:
    return f"whsec_{secrets.token_urlsafe(24)}"


def normalize_webhook_events(events: Sequence[str] | None) -> list[str]:
    if not events:
        return list(SUPPORTED_WEBHOOK_EVENTS)

    normalized: list[str] = []
    seen: set[str] = set()
    for raw_event in events:
        event = raw_event.strip()
        if not event:
            continue
        if event not in SUPPORTED_WEBHOOK_EVENTS:
            raise ValueError(f"Unsupported webhook event: {event}")
        if event in seen:
            continue
        seen.add(event)
        normalized.append(event)

    if not normalized:
        return list(SUPPORTED_WEBHOOK_EVENTS)
    return normalized
