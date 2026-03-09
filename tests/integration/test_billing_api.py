"""Integration tests for billing API endpoints."""

from httpx import AsyncClient

from backend.src.saas_starter.api.v1.billing import get_stripe_service
from backend.src.saas_starter.main import app
from tests.conftest import seed_tenant_and_user

# ---------------------------------------------------------------------------
# Mock Stripe
# ---------------------------------------------------------------------------


class _MockStripeService:
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


app.dependency_overrides[get_stripe_service] = _MockStripeService


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_get_plans_returns_three_plans(client: AsyncClient) -> None:
    """GET /billing/plans returns free, starter, pro."""
    resp = await client.get("/api/v1/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()
    assert len(plans) == 3
    names = [p["name"] for p in plans]
    assert "free" in names
    assert "starter" in names
    assert "pro" in names


async def test_subscribe_requires_auth(client: AsyncClient) -> None:
    """POST /billing/subscribe without token returns 401/422."""
    resp = await client.post(
        "/api/v1/billing/subscribe",
        json={"price_id": "price_test"},
    )
    assert resp.status_code in (401, 422)


async def test_get_current_plan_shows_free_for_new_tenant(client: AsyncClient) -> None:
    """New tenant without subscription shows free plan."""
    _t, _u, token = await seed_tenant_and_user(email="plan@test.com", tenant_slug="plan-test")
    resp = await client.get("/api/v1/billing/current", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["plan"] == "free"
    assert body["status"] == "active"


async def test_cancel_requires_active_subscription(client: AsyncClient) -> None:
    """POST /billing/cancel without subscription returns 502 (StripeError)."""
    _t, _u, token = await seed_tenant_and_user(email="cancel@test.com", tenant_slug="cancel-test")
    resp = await client.post("/api/v1/billing/cancel", headers=_auth(token))
    assert resp.status_code == 502
    assert "No active subscription" in resp.json()["detail"]
