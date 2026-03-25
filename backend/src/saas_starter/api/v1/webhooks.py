"""Stripe webhook handler — NO auth required, signature-verified."""

import hashlib
import hmac
import time

from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select

from backend.src.saas_starter.api.deps import DBSession
from backend.src.saas_starter.core.config import settings
from backend.src.saas_starter.models.subscription import Subscription, SubscriptionStatus

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> dict | None:
    """Verify Stripe webhook signature (v1 scheme) and return the parsed event.

    Returns None if the signature is invalid.
    """
    import json

    elements = dict(pair.split("=", 1) for pair in sig_header.split(",") if "=" in pair)
    timestamp = elements.get("t", "")
    signature = elements.get("v1", "")

    if not timestamp or not signature:
        return None

    # Tolerance: reject events older than 5 minutes
    if abs(time.time() - int(timestamp)) > 300:
        return None

    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, signature):
        return None

    return json.loads(payload)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: DBSession,
    stripe_signature: str = Header(..., alias="Stripe-Signature"),
) -> JSONResponse:
    """Handle Stripe webhook events."""
    body = await request.body()
    event = verify_stripe_signature(body, stripe_signature, settings.stripe_webhook_secret)

    if event is None:
        return JSONResponse(status_code=400, content={"detail": "Invalid signature"})

    event_type = event.get("type", "")
    data_object = event.get("data", {}).get("object", {})

    if event_type == "customer.subscription.updated":
        await _handle_subscription_updated(db, data_object)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(db, data_object)
    elif event_type == "invoice.payment_succeeded":
        await _handle_payment_succeeded(db, data_object)
    elif event_type == "invoice.payment_failed":
        await _handle_payment_failed(db, data_object)

    return JSONResponse(status_code=200, content={"received": True})


_STRIPE_TO_STATUS: dict[str, SubscriptionStatus] = {s.value: s for s in SubscriptionStatus}


async def _handle_subscription_updated(db, data: dict) -> None:
    """Update subscription status from Stripe event."""
    stripe_sub_id = data.get("id", "")
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return

    raw_status = data.get("status", "")
    mapped_status = _STRIPE_TO_STATUS.get(raw_status)
    if mapped_status is not None:
        sub.status = mapped_status
    await db.flush()


async def _handle_subscription_deleted(db, data: dict) -> None:
    """Mark subscription as canceled."""
    stripe_sub_id = data.get("id", "")
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = SubscriptionStatus.CANCELED
        await db.flush()


async def _handle_payment_succeeded(db, data: dict) -> None:
    """Mark subscription as active after successful payment."""
    stripe_sub_id = data.get("subscription", "")
    if not stripe_sub_id:
        return
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = SubscriptionStatus.ACTIVE
        await db.flush()


async def _handle_payment_failed(db, data: dict) -> None:
    """Mark subscription as past_due after failed payment."""
    stripe_sub_id = data.get("subscription", "")
    if not stripe_sub_id:
        return
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == stripe_sub_id)
    )
    sub = result.scalar_one_or_none()
    if sub:
        sub.status = SubscriptionStatus.PAST_DUE
        await db.flush()
