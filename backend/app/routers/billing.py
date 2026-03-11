from __future__ import annotations

import asyncio
import datetime as dt
from functools import partial
from typing import Any
from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing import get_usage_limit_states, has_soft_limit_violation
from app.config import Settings
from app.deps import get_db, get_session_user, get_settings_dep
from app.middleware.error_handler import APIError
from app.models import BillingEvent, User, Workspace, WorkspaceMember
from app.persistence import ensure_workspace
from app.schemas.auth import UserOut
from app.schemas.billing import (
    BillingCheckoutSessionCreate,
    BillingPortalSessionCreate,
    BillingSessionOut,
    BillingSubscriptionOut,
    BillingUsageLimitOut,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/billing", tags=["Billing"])

ACTIVE_SUBSCRIPTION_STATUSES = {"trialing", "active", "past_due", "unpaid", "incomplete", "paused"}


def _coerce_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def _coerce_metadata(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}

    output: dict[str, str] = {}
    for key, entry in value.items():
        if entry is None:
            continue
        output[str(key)] = str(entry)
    return output


def _stripe_value(data: Any, key: str, default: Any = None) -> Any:
    if isinstance(data, dict):
        return data.get(key, default)
    return getattr(data, key, default)


def _stripe_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    to_dict_recursive = getattr(value, "to_dict_recursive", None)
    if callable(to_dict_recursive):
        payload = to_dict_recursive()
        if isinstance(payload, dict):
            return payload

    return {}


def _timestamp_to_datetime(value: Any) -> dt.datetime | None:
    if value is None:
        return None

    try:
        return dt.datetime.fromtimestamp(int(value), tz=dt.UTC)
    except (OSError, TypeError, ValueError):
        return None


def _extract_subscription_price_id(subscription: Any) -> str | None:
    items = _stripe_value(subscription, "items")
    data = _stripe_value(items, "data", []) if items is not None else []
    if not isinstance(data, list) or not data:
        return None

    price = _stripe_value(data[0], "price")
    return _coerce_text(_stripe_value(price, "id"))


def _require_stripe_configuration(settings: Settings) -> None:
    if not settings.stripe_secret_key:
        raise APIError(
            status_code=503,
            code="stripe_config_missing",
            message="Stripe is not configured for this environment.",
        )

    stripe.api_key = settings.stripe_secret_key


def _checkout_success_url(settings: Settings, explicit: str | None) -> str:
    if explicit:
        return explicit
    if settings.stripe_checkout_success_url:
        return settings.stripe_checkout_success_url
    return f"{settings.app_url}/workspace/settings?billing=success"


def _checkout_cancel_url(settings: Settings, explicit: str | None) -> str:
    if explicit:
        return explicit
    if settings.stripe_checkout_cancel_url:
        return settings.stripe_checkout_cancel_url
    return f"{settings.app_url}/pricing?billing=cancelled"


def _portal_return_url(settings: Settings, explicit: str | None) -> str:
    if explicit:
        return explicit
    if settings.stripe_portal_return_url:
        return settings.stripe_portal_return_url
    return f"{settings.app_url}/workspace/settings"


async def _get_workspace_row(session: AsyncSession, workspace_id: UUID, user_id: UUID):
    row = (
        await session.execute(
            select(
                Workspace.id,
                Workspace.name,
                Workspace.plan,
                Workspace.stripe_customer_id,
                Workspace.stripe_subscription_id,
                Workspace.stripe_price_id,
                Workspace.subscription_status,
                Workspace.cancel_at_period_end,
                Workspace.current_period_end,
                WorkspaceMember.role.label("membership_role"),
                User.email.label("owner_email"),
                User.name.label("owner_name"),
            )
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .join(User, User.id == Workspace.owner_id)
            .where(Workspace.id == workspace_id)
            .where(WorkspaceMember.user_id == user_id)
        )
    ).one_or_none()

    if row is None:
        raise APIError(status_code=404, code="workspace_not_found", message="Workspace not found.")

    return row


def _require_billing_role(row: Any) -> None:
    if row.membership_role not in {"owner", "admin"}:
        raise APIError(
            status_code=403,
            code="billing_access_denied",
            message="Only workspace owners or admins can manage billing.",
        )


async def _serialize_subscription(
    session: AsyncSession,
    row: Any,
    *,
    settings: Settings,
) -> BillingSubscriptionOut:
    usage_limits = await get_usage_limit_states(
        session,
        workspace_id=row.id,
        plan=row.plan,
        settings=settings,
    )

    return BillingSubscriptionOut(
        workspace_id=row.id,
        plan=row.plan,
        subscription_status=row.subscription_status,
        stripe_customer_id=row.stripe_customer_id,
        stripe_subscription_id=row.stripe_subscription_id,
        stripe_price_id=row.stripe_price_id,
        cancel_at_period_end=row.cancel_at_period_end,
        current_period_end=row.current_period_end,
        portal_available=bool(settings.stripe_secret_key and row.stripe_customer_id),
        usage_limits=[
            BillingUsageLimitOut(
                key=limit.key,
                label=limit.label,
                window=limit.window,
                used=limit.used,
                limit=limit.limit,
                remaining=limit.remaining,
                soft_limited=limit.soft_limited,
            )
            for limit in usage_limits
        ],
        overage_warning=has_soft_limit_violation(usage_limits),
    )


def _subscription_workspace_plan(
    *,
    status: str,
    price_id: str | None,
    metadata: dict[str, str],
    current_plan: str,
    settings: Settings,
) -> str:
    if status in {"canceled", "incomplete_expired"}:
        return "free"

    metadata_plan = metadata.get("plan")
    if metadata_plan in {"pro", "team", "enterprise"}:
        return metadata_plan

    if price_id and settings.stripe_pro_price_id and price_id == settings.stripe_pro_price_id:
        return "pro"

    if current_plan in {"pro", "team", "enterprise"}:
        return current_plan

    return "free"


def _subscription_updates(subscription: Any, *, current_plan: str, settings: Settings) -> dict[str, Any]:
    metadata = _coerce_metadata(_stripe_value(subscription, "metadata", {}))
    price_id = _extract_subscription_price_id(subscription)
    status = _coerce_text(_stripe_value(subscription, "status")) or "active"
    return {
        "plan": _subscription_workspace_plan(
            status=status,
            price_id=price_id,
            metadata=metadata,
            current_plan=current_plan,
            settings=settings,
        ),
        "stripe_customer_id": _coerce_text(_stripe_value(subscription, "customer")),
        "stripe_subscription_id": _coerce_text(_stripe_value(subscription, "id")),
        "stripe_price_id": price_id,
        "subscription_status": status,
        "cancel_at_period_end": bool(_stripe_value(subscription, "cancel_at_period_end", False)),
        "current_period_end": _timestamp_to_datetime(_stripe_value(subscription, "current_period_end")),
    }


async def _record_billing_event(
    session: AsyncSession,
    *,
    event_id: str,
    event_type: str,
    workspace_id: UUID | None,
    stripe_customer_id: str | None,
    stripe_subscription_id: str | None,
    payload: dict[str, Any],
) -> bool:
    result = await session.execute(
        pg_insert(BillingEvent)
        .values(
            stripe_event_id=event_id,
            event_type=event_type,
            workspace_id=workspace_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            payload=payload,
        )
        .on_conflict_do_nothing(index_elements=[BillingEvent.stripe_event_id])
    )
    return (result.rowcount or 0) > 0


def _workspace_id_from_metadata(payload: Any) -> UUID | None:
    metadata = _coerce_metadata(_stripe_value(payload, "metadata", {}))
    raw_workspace_id = metadata.get("workspace_id")
    if not raw_workspace_id:
        return None

    try:
        return UUID(raw_workspace_id)
    except ValueError:
        return None


async def _resolve_workspace_id_from_stripe_references(
    session: AsyncSession,
    *,
    stripe_customer_id: str | None,
    stripe_subscription_id: str | None,
) -> UUID | None:
    statement = select(Workspace.id)
    if stripe_subscription_id:
        value = (
            await session.execute(
                statement.where(Workspace.stripe_subscription_id == stripe_subscription_id).limit(1)
            )
        ).scalar_one_or_none()
        if value is not None:
            return value

    if stripe_customer_id:
        return (
            await session.execute(statement.where(Workspace.stripe_customer_id == stripe_customer_id).limit(1))
        ).scalar_one_or_none()

    return None


async def _apply_checkout_session_completed(
    session: AsyncSession,
    *,
    checkout_session: Any,
    workspace_id: UUID | None,
) -> UUID | None:
    resolved_workspace_id = workspace_id
    stripe_customer_id = _coerce_text(_stripe_value(checkout_session, "customer"))
    stripe_subscription_id = _coerce_text(_stripe_value(checkout_session, "subscription"))
    metadata = _coerce_metadata(_stripe_value(checkout_session, "metadata", {}))

    if resolved_workspace_id is None:
        resolved_workspace_id = await _resolve_workspace_id_from_stripe_references(
            session,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )

    if resolved_workspace_id is None:
        return None

    updates: dict[str, Any] = {}
    if stripe_customer_id:
        updates["stripe_customer_id"] = stripe_customer_id
    if stripe_subscription_id:
        updates["stripe_subscription_id"] = stripe_subscription_id
    if metadata.get("plan") in {"pro", "team", "enterprise"}:
        updates["plan"] = metadata["plan"]
    payment_status = _coerce_text(_stripe_value(checkout_session, "payment_status"))
    if payment_status == "paid":
        updates["subscription_status"] = "active"
    elif stripe_subscription_id:
        updates["subscription_status"] = "incomplete"

    if updates:
        await session.execute(update(Workspace).where(Workspace.id == resolved_workspace_id).values(**updates))

    return resolved_workspace_id


async def _apply_subscription_event(
    session: AsyncSession,
    *,
    subscription: Any,
    workspace_id: UUID | None,
    settings: Settings,
) -> UUID | None:
    stripe_customer_id = _coerce_text(_stripe_value(subscription, "customer"))
    stripe_subscription_id = _coerce_text(_stripe_value(subscription, "id"))
    resolved_workspace_id = workspace_id

    if resolved_workspace_id is None:
        resolved_workspace_id = await _resolve_workspace_id_from_stripe_references(
            session,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )

    if resolved_workspace_id is None:
        return None

    current_plan = (
        await session.execute(select(Workspace.plan).where(Workspace.id == resolved_workspace_id))
    ).scalar_one_or_none()
    if current_plan is None:
        return None

    await session.execute(
        update(Workspace)
        .where(Workspace.id == resolved_workspace_id)
        .values(**_subscription_updates(subscription, current_plan=current_plan, settings=settings))
    )
    return resolved_workspace_id


@router.get("/subscription", response_model=BillingSubscriptionOut)
async def get_subscription(
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> BillingSubscriptionOut:
    await ensure_workspace(session, current_user)
    row = await _get_workspace_row(session, current_user.workspace_id, current_user.id)
    return await _serialize_subscription(session, row, settings=settings)


@router.post("/checkout-session", response_model=BillingSessionOut, status_code=status.HTTP_201_CREATED)
async def create_checkout_session(
    payload: BillingCheckoutSessionCreate,
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> BillingSessionOut:
    await ensure_workspace(session, current_user)
    row = await _get_workspace_row(session, current_user.workspace_id, current_user.id)
    _require_billing_role(row)
    _require_stripe_configuration(settings)

    if not settings.stripe_pro_price_id:
        raise APIError(
            status_code=503,
            code="stripe_price_missing",
            message="The Stripe Pro price is not configured.",
        )

    if row.stripe_subscription_id and row.subscription_status in ACTIVE_SUBSCRIPTION_STATUSES:
        raise APIError(
            status_code=409,
            code="billing_subscription_exists",
            message="This workspace already has an active Stripe subscription.",
        )

    stripe_customer_id = row.stripe_customer_id
    if not stripe_customer_id:
        customer = await asyncio.to_thread(
            partial(
                stripe.Customer.create,
                email=row.owner_email or current_user.email,
                name=row.name,
                metadata={"workspace_id": str(row.id)},
            )
        )
        stripe_customer_id = _coerce_text(_stripe_value(customer, "id"))
        if not stripe_customer_id:
            raise APIError(
                status_code=502,
                code="stripe_customer_create_failed",
                message="Stripe did not return a customer identifier.",
            )
        await session.execute(
            update(Workspace)
            .where(Workspace.id == row.id)
            .values(stripe_customer_id=stripe_customer_id)
        )
        await session.commit()

    checkout_session = await asyncio.to_thread(
        partial(
            stripe.checkout.Session.create,
            mode="subscription",
            customer=stripe_customer_id,
            success_url=_checkout_success_url(settings, payload.success_url),
            cancel_url=_checkout_cancel_url(settings, payload.cancel_url),
            allow_promotion_codes=True,
            client_reference_id=str(row.id),
            line_items=[{"price": settings.stripe_pro_price_id, "quantity": 1}],
            metadata={"workspace_id": str(row.id), "plan": payload.plan},
            subscription_data={"metadata": {"workspace_id": str(row.id), "plan": payload.plan}},
        )
    )
    session_id = _coerce_text(_stripe_value(checkout_session, "id"))
    url = _coerce_text(_stripe_value(checkout_session, "url"))
    if not session_id or not url:
        raise APIError(
            status_code=502,
            code="stripe_checkout_create_failed",
            message="Stripe did not return a checkout session URL.",
        )

    return BillingSessionOut(id=session_id, url=url)


@router.post("/portal-session", response_model=BillingSessionOut)
async def create_portal_session(
    payload: BillingPortalSessionCreate,
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> BillingSessionOut:
    await ensure_workspace(session, current_user)
    row = await _get_workspace_row(session, current_user.workspace_id, current_user.id)
    _require_billing_role(row)
    _require_stripe_configuration(settings)

    if not row.stripe_customer_id:
        raise APIError(
            status_code=400,
            code="billing_portal_unavailable",
            message="This workspace does not have a Stripe customer yet.",
        )

    portal_session = await asyncio.to_thread(
        partial(
            stripe.billing_portal.Session.create,
            customer=row.stripe_customer_id,
            return_url=_portal_return_url(settings, payload.return_url),
        )
    )
    session_id = _coerce_text(_stripe_value(portal_session, "id"))
    url = _coerce_text(_stripe_value(portal_session, "url"))
    if not session_id or not url:
        raise APIError(
            status_code=502,
            code="stripe_portal_create_failed",
            message="Stripe did not return a billing portal URL.",
        )

    return BillingSessionOut(id=session_id, url=url)


@router.post("/subscription/cancel", response_model=BillingSubscriptionOut)
async def cancel_subscription(
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> BillingSubscriptionOut:
    await ensure_workspace(session, current_user)
    row = await _get_workspace_row(session, current_user.workspace_id, current_user.id)
    _require_billing_role(row)
    _require_stripe_configuration(settings)

    if not row.stripe_subscription_id:
        raise APIError(
            status_code=400,
            code="billing_subscription_missing",
            message="This workspace does not have an active Stripe subscription.",
        )

    subscription = await asyncio.to_thread(
        partial(
            stripe.Subscription.modify,
            row.stripe_subscription_id,
            cancel_at_period_end=True,
        )
    )
    await _apply_subscription_event(
        session,
        subscription=subscription,
        workspace_id=row.id,
        settings=settings,
    )
    await session.commit()
    return await _serialize_subscription(
        session,
        await _get_workspace_row(session, current_user.workspace_id, current_user.id),
        settings=settings,
    )


@router.post("/subscription/reactivate", response_model=BillingSubscriptionOut)
async def reactivate_subscription(
    current_user: UserOut = Depends(get_session_user),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> BillingSubscriptionOut:
    await ensure_workspace(session, current_user)
    row = await _get_workspace_row(session, current_user.workspace_id, current_user.id)
    _require_billing_role(row)
    _require_stripe_configuration(settings)

    if not row.stripe_subscription_id:
        raise APIError(
            status_code=400,
            code="billing_subscription_missing",
            message="This workspace does not have an active Stripe subscription.",
        )

    subscription = await asyncio.to_thread(
        partial(
            stripe.Subscription.modify,
            row.stripe_subscription_id,
            cancel_at_period_end=False,
        )
    )
    await _apply_subscription_event(
        session,
        subscription=subscription,
        workspace_id=row.id,
        settings=settings,
    )
    await session.commit()
    return await _serialize_subscription(
        session,
        await _get_workspace_row(session, current_user.workspace_id, current_user.id),
        settings=settings,
    )


@router.post("/webhooks/stripe", response_model=MessageResponse)
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="stripe-signature"),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
) -> MessageResponse:
    if not settings.stripe_webhook_secret:
        raise APIError(
            status_code=503,
            code="stripe_webhook_secret_missing",
            message="The Stripe webhook signing secret is not configured.",
        )
    if not stripe_signature:
        raise APIError(
            status_code=400,
            code="stripe_signature_missing",
            message="The Stripe webhook signature header is required.",
        )

    _require_stripe_configuration(settings)
    payload = await request.body()
    try:
        event = await asyncio.to_thread(
            partial(
                stripe.Webhook.construct_event,
                payload,
                stripe_signature,
                settings.stripe_webhook_secret,
            )
        )
    except ValueError as exc:
        raise APIError(
            status_code=400,
            code="stripe_payload_invalid",
            message="The Stripe webhook payload was invalid.",
            details=[{"reason": str(exc)}],
        ) from exc
    except stripe.error.SignatureVerificationError as exc:
        raise APIError(
            status_code=400,
            code="stripe_signature_invalid",
            message="The Stripe webhook signature could not be verified.",
            details=[{"reason": str(exc)}],
        ) from exc

    event_id = _coerce_text(_stripe_value(event, "id"))
    event_type = _coerce_text(_stripe_value(event, "type"))
    data = _stripe_value(_stripe_value(event, "data", {}), "object", {})
    if not event_id or not event_type:
        raise APIError(
            status_code=400,
            code="stripe_event_invalid",
            message="The Stripe webhook payload is missing required fields.",
        )

    stripe_customer_id = _coerce_text(_stripe_value(data, "customer"))
    stripe_subscription_id = _coerce_text(_stripe_value(data, "subscription"))
    if event_type.startswith("customer.subscription."):
        stripe_subscription_id = stripe_subscription_id or _coerce_text(_stripe_value(data, "id"))

    workspace_id = _workspace_id_from_metadata(data)
    if workspace_id is None:
        workspace_id = await _resolve_workspace_id_from_stripe_references(
            session,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )

    inserted = await _record_billing_event(
        session,
        event_id=event_id,
        event_type=event_type,
        workspace_id=workspace_id,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
        payload=_stripe_payload(event),
    )
    if not inserted:
        await session.commit()
        return MessageResponse(message="Stripe event already processed.")

    if event_type == "checkout.session.completed":
        workspace_id = await _apply_checkout_session_completed(
            session,
            checkout_session=data,
            workspace_id=workspace_id,
        )
    elif event_type in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        workspace_id = await _apply_subscription_event(
            session,
            subscription=data,
            workspace_id=workspace_id,
            settings=settings,
        )

    await session.execute(
        update(BillingEvent)
        .where(BillingEvent.stripe_event_id == event_id)
        .values(
            workspace_id=workspace_id,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            processed_at=dt.datetime.now(dt.UTC),
        )
    )
    await session.commit()
    return MessageResponse(message="Stripe event received.")
