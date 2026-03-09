"""Stripe billing service — all calls via httpx async (ADR-005)."""

import uuid

import httpx

from backend.src.saas_starter.core.config import settings

_BASE_URL = "https://api.stripe.com/v1"


class StripeService:
    """Async wrapper around the Stripe REST API."""

    def __init__(self, secret_key: str | None = None) -> None:
        self.secret_key = secret_key or settings.stripe_secret_key

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.secret_key}"}

    async def create_customer(self, tenant_id: uuid.UUID, email: str, name: str) -> str:
        """Create a Stripe customer and return the customer ID."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_BASE_URL}/customers",
                headers=self._headers(),
                data={
                    "email": email,
                    "name": name,
                    "metadata[tenant_id]": str(tenant_id),
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["id"]

    async def create_subscription(self, customer_id: str, price_id: str) -> dict:
        """Create a Stripe subscription."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_BASE_URL}/subscriptions",
                headers=self._headers(),
                data={
                    "customer": customer_id,
                    "items[0][price]": price_id,
                    "payment_behavior": "default_incomplete",
                    "expand[]": "latest_invoice.payment_intent",
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def cancel_subscription(self, stripe_subscription_id: str) -> None:
        """Cancel a Stripe subscription."""
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{_BASE_URL}/subscriptions/{stripe_subscription_id}",
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()

    async def get_subscription(self, stripe_subscription_id: str) -> dict:
        """Retrieve a Stripe subscription."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_BASE_URL}/subscriptions/{stripe_subscription_id}",
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()

    async def create_billing_portal_session(self, customer_id: str, return_url: str) -> str:
        """Create a Stripe billing portal session and return the URL."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_BASE_URL}/billing_portal/sessions",
                headers=self._headers(),
                data={
                    "customer": customer_id,
                    "return_url": return_url,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["url"]
