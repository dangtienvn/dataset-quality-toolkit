"""End-to-end integration tests covering the complete SaaS flow."""

from httpx import AsyncClient

from backend.src.saas_starter.api.v1.billing import get_stripe_service
from backend.src.saas_starter.main import app
from tests.conftest import seed_tenant_and_user

# ---------------------------------------------------------------------------
# Mock Stripe (reuse pattern from test_billing_api)
# ---------------------------------------------------------------------------


class _MockStripeService:
    async def create_customer(self, tenant_id, email, name):
        return "cus_flow_123"

    async def create_subscription(self, customer_id, price_id):
        return {
            "id": "sub_flow_456",
            "status": "active",
            "latest_invoice": {"hosted_invoice_url": "https://checkout.stripe.com/flow"},
        }

    async def cancel_subscription(self, stripe_subscription_id):
        pass

    async def get_subscription(self, stripe_subscription_id):
        return {"id": stripe_subscription_id, "status": "active"}

    async def create_billing_portal_session(self, customer_id, return_url):
        return "https://billing.stripe.com/portal/flow"


app.dependency_overrides[get_stripe_service] = _MockStripeService


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_complete_saas_journey(client: AsyncClient) -> None:
    """Full user journey: register → chat → usage → dashboard → export."""
    # 1. Register
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "journey@test.com",
            "password": "pass123",
            "full_name": "Journey User",
            "tenant_name": "Journey Co",
            "tenant_slug": "journey-co",
        },
    )
    assert resp.status_code == 201
    tokens = resp.json()
    token = tokens["access_token"]
    headers = _auth(token)

    # 2. Chat with AI (MockLLM)
    resp = await client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["content"]

    # 3. Usage tracked
    resp = await client.get("/api/v1/ai/usage", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["calls_count"] >= 1

    # 4. Admin dashboard
    resp = await client.get("/api/v1/admin/dashboard", headers=headers)
    assert resp.status_code == 200
    dash = resp.json()
    assert dash["tenant"]["plan"] == "free"
    assert dash["users"]["total"] == 1

    # 5. GDPR export
    resp = await client.get("/api/v1/gdpr/export", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "users" in data
    assert "ai_usages" in data
    assert len(data["users"]) == 1
    assert len(data["ai_usages"]) >= 1


async def test_multi_tenant_isolation(client: AsyncClient) -> None:
    """Two tenants cannot see each other's data."""
    # Tenant A
    resp_a = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "a@iso.com",
            "password": "pass123",
            "full_name": "User A",
            "tenant_name": "Tenant A",
            "tenant_slug": "tenant-a",
        },
    )
    assert resp_a.status_code == 201
    token_a = resp_a.json()["access_token"]

    # Tenant A chats
    await client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Hello from A"}]},
        headers=_auth(token_a),
    )

    # Tenant B
    resp_b = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "b@iso.com",
            "password": "pass123",
            "full_name": "User B",
            "tenant_name": "Tenant B",
            "tenant_slug": "tenant-b",
        },
    )
    assert resp_b.status_code == 201
    token_b = resp_b.json()["access_token"]

    # Tenant B chats
    await client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Hello from B"}]},
        headers=_auth(token_b),
    )

    # Tenant A usage — only A's data
    resp = await client.get("/api/v1/ai/usage", headers=_auth(token_a))
    assert resp.status_code == 200
    assert resp.json()["calls_count"] == 1

    # Tenant B usage — only B's data
    resp = await client.get("/api/v1/ai/usage", headers=_auth(token_b))
    assert resp.status_code == 200
    assert resp.json()["calls_count"] == 1

    # Tenant A users — only A's user
    resp = await client.get("/api/v1/users", headers=_auth(token_a))
    assert resp.status_code == 200
    users_a = resp.json()["users"]
    assert len(users_a) == 1
    assert users_a[0]["email"] == "a@iso.com"

    # Tenant B users — only B's user
    resp = await client.get("/api/v1/users", headers=_auth(token_b))
    assert resp.status_code == 200
    users_b = resp.json()["users"]
    assert len(users_b) == 1
    assert users_b[0]["email"] == "b@iso.com"


async def test_subscription_flow(client: AsyncClient) -> None:
    """Subscribe and cancel flow with MockStripeService."""
    _t, _u, token = await seed_tenant_and_user(email="sub-flow@test.com", tenant_slug="sub-flow")
    headers = _auth(token)

    # New tenant → free plan
    resp = await client.get("/api/v1/billing/current", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["plan"] == "free"

    # Subscribe — now also creates a Subscription row in DB
    resp = await client.post(
        "/api/v1/billing/subscribe",
        json={"price_id": "price_starter_test"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["checkout_url"]

    # Cancel — uses the subscription created by subscribe
    resp = await client.post("/api/v1/billing/cancel", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "subscription canceled"
