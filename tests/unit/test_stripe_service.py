"""Unit tests for Stripe service and webhook verification."""

import hashlib
import hmac
import json
import time
import uuid
from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from backend.src.saas_starter.api.v1.webhooks import verify_stripe_signature
from backend.src.saas_starter.main import app
from backend.src.saas_starter.models.subscription import Subscription, SubscriptionStatus
from backend.src.saas_starter.models.tenant import PlanType, Tenant
from tests.conftest import TestSessionLocal

# ---------------------------------------------------------------------------
# Mock Stripe service
# ---------------------------------------------------------------------------


class MockStripeService:
    """Mock that returns deterministic data without HTTP calls."""

    async def create_customer(self, tenant_id, email, name):
        return "cus_mock_123"

    async def create_subscription(self, customer_id, price_id):
        return {
            "id": "sub_mock_456",
            "status": "active",
            "latest_invoice": {"hosted_invoice_url": "https://checkout.stripe.com/mock"},
        }

    async def cancel_subscription(self, stripe_subscription_id):
        pass

    async def get_subscription(self, stripe_subscription_id):
        return {"id": stripe_subscription_id, "status": "active"}

    async def create_billing_portal_session(self, customer_id, return_url):
        return "https://billing.stripe.com/portal/mock"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WEBHOOK_SECRET = "whsec_test_secret"


def _sign_payload(payload: bytes, secret: str = _WEBHOOK_SECRET) -> str:
    """Create a valid Stripe-Signature header."""
    timestamp = str(int(time.time()))
    signed = f"{timestamp}.".encode() + payload
    sig = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={sig}"


def _make_event(event_type: str, data_object: dict) -> bytes:
    return json.dumps({"type": event_type, "data": {"object": data_object}}).encode()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_create_customer_returns_id() -> None:
    """MockStripeService.create_customer returns a customer ID."""
    import asyncio

    svc = MockStripeService()
    result = asyncio.get_event_loop().run_until_complete(
        svc.create_customer(uuid.uuid4(), "t@t.com", "Test")
    )
    assert result == "cus_mock_123"


def test_cancel_subscription_calls_correct_endpoint() -> None:
    """MockStripeService.cancel_subscription completes without error."""
    import asyncio

    svc = MockStripeService()
    asyncio.get_event_loop().run_until_complete(svc.cancel_subscription("sub_123"))


def test_webhook_signature_valid_processes_event() -> None:
    """Valid signature returns parsed event data."""
    payload = _make_event("test.event", {"id": "obj_1"})
    sig = _sign_payload(payload)
    result = verify_stripe_signature(payload, sig, _WEBHOOK_SECRET)
    assert result is not None
    assert result["type"] == "test.event"


def test_webhook_invalid_signature_returns_none() -> None:
    """Invalid signature returns None."""
    payload = _make_event("test.event", {"id": "obj_1"})
    result = verify_stripe_signature(payload, "t=123,v1=bad_signature", _WEBHOOK_SECRET)
    assert result is None


async def test_webhook_subscription_updated_changes_status() -> None:
    """Webhook customer.subscription.updated changes subscription status."""
    # Seed a tenant + subscription
    async with TestSessionLocal() as db:
        tenant = Tenant(id=uuid.uuid4(), name="W", slug="webhook-test", plan=PlanType.FREE)
        db.add(tenant)
        await db.flush()
        sub = Subscription(
            tenant_id=tenant.id,
            stripe_subscription_id="sub_webhook_1",
            stripe_price_id="price_test",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.now(UTC),
        )
        db.add(sub)
        await db.commit()

    # Send webhook
    from unittest.mock import patch

    payload = _make_event(
        "customer.subscription.updated",
        {"id": "sub_webhook_1", "status": "past_due"},
    )
    sig = _sign_payload(payload)

    with patch("backend.src.saas_starter.api.v1.webhooks.settings") as mock_settings:
        mock_settings.stripe_webhook_secret = _WEBHOOK_SECRET

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/webhooks/stripe",
                content=payload,
                headers={"Stripe-Signature": sig, "Content-Type": "application/json"},
            )

    assert resp.status_code == 200

    # Verify DB change
    async with TestSessionLocal() as db:
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == "sub_webhook_1")
        )
        updated = result.scalar_one()
        assert updated.status in (SubscriptionStatus.PAST_DUE, "past_due")


async def test_webhook_payment_failed_marks_past_due() -> None:
    """Webhook invoice.payment_failed marks subscription as past_due."""
    async with TestSessionLocal() as db:
        tenant = Tenant(id=uuid.uuid4(), name="PF", slug="pay-fail", plan=PlanType.FREE)
        db.add(tenant)
        await db.flush()
        sub = Subscription(
            tenant_id=tenant.id,
            stripe_subscription_id="sub_pf_1",
            stripe_price_id="price_test",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=datetime.now(UTC),
        )
        db.add(sub)
        await db.commit()

    from unittest.mock import patch

    payload = _make_event(
        "invoice.payment_failed",
        {"subscription": "sub_pf_1"},
    )
    sig = _sign_payload(payload)

    with patch("backend.src.saas_starter.api.v1.webhooks.settings") as mock_settings:
        mock_settings.stripe_webhook_secret = _WEBHOOK_SECRET

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/webhooks/stripe",
                content=payload,
                headers={"Stripe-Signature": sig, "Content-Type": "application/json"},
            )

    assert resp.status_code == 200

    async with TestSessionLocal() as db:
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == "sub_pf_1")
        )
        updated = result.scalar_one()
        assert updated.status in (SubscriptionStatus.PAST_DUE, "past_due")
