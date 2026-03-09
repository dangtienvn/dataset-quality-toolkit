"""Billing endpoints: plans, subscribe, cancel, portal, current plan."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.src.saas_starter.api.deps import CurrentUser, DBSession
from backend.src.saas_starter.core.config import settings
from backend.src.saas_starter.core.exceptions import StripeError
from backend.src.saas_starter.models.subscription import Subscription, SubscriptionStatus
from backend.src.saas_starter.models.tenant import Tenant
from backend.src.saas_starter.schemas.billing import (
    CurrentPlanResponse,
    PlanInfo,
    SubscribeRequest,
    SubscribeResponse,
)
from backend.src.saas_starter.services.stripe_service import StripeService

router = APIRouter(prefix="/billing", tags=["billing"])


def get_stripe_service() -> StripeService:
    """Dependency for StripeService (overridable in tests)."""
    return StripeService()


StripeDep = Annotated[StripeService, Depends(get_stripe_service)]

_PLANS = [
    PlanInfo(
        name="free",
        price_usd=0,
        features=["100 AI calls/month", "1 user", "Community support"],
        price_id="",
    ),
    PlanInfo(
        name="starter",
        price_usd=29,
        features=["5,000 AI calls/month", "5 users", "Email support", "Priority models"],
        price_id=settings.stripe_price_id_starter,
    ),
    PlanInfo(
        name="pro",
        price_usd=99,
        features=[
            "Unlimited AI calls",
            "Unlimited users",
            "Priority support",
            "All models",
            "Custom integrations",
        ],
        price_id=settings.stripe_price_id_pro,
    ),
]


@router.get("/plans", response_model=list[PlanInfo])
async def get_plans() -> list[PlanInfo]:
    """Return available subscription plans."""
    return _PLANS


@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(
    req: SubscribeRequest,
    user: CurrentUser,
    db: DBSession,
    stripe: StripeDep,
) -> SubscribeResponse:
    """Create a Stripe subscription for the current tenant."""
    # Get tenant
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one()

    # Ensure Stripe customer exists
    customer_id = tenant.stripe_customer_id
    if not customer_id:
        try:
            customer_id = await stripe.create_customer(
                tenant_id=tenant.id, email=user.email, name=tenant.name
            )
        except Exception as exc:
            raise StripeError(f"Failed to create customer: {exc}") from exc
        tenant.stripe_customer_id = customer_id
        await db.flush()

    # Create subscription
    try:
        sub_data = await stripe.create_subscription(customer_id, req.price_id)
    except Exception as exc:
        raise StripeError(f"Failed to create subscription: {exc}") from exc

    # For simplicity, return a checkout URL placeholder
    checkout_url = sub_data.get("latest_invoice", {}).get(
        "hosted_invoice_url", f"https://checkout.stripe.com/{sub_data.get('id', '')}"
    )

    return SubscribeResponse(checkout_url=checkout_url)


@router.post("/cancel")
async def cancel_subscription(
    user: CurrentUser,
    db: DBSession,
    stripe: StripeDep,
) -> dict:
    """Cancel the active subscription for the current tenant."""
    result = await db.execute(select(Subscription).where(Subscription.tenant_id == user.tenant_id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise StripeError("No active subscription found")

    try:
        await stripe.cancel_subscription(sub.stripe_subscription_id)
    except Exception as exc:
        raise StripeError(f"Failed to cancel subscription: {exc}") from exc

    sub.status = SubscriptionStatus.CANCELED
    await db.flush()
    return {"message": "subscription canceled"}


@router.get("/portal")
async def billing_portal(user: CurrentUser, db: DBSession, stripe: StripeDep) -> dict:
    """Create a Stripe billing portal session."""
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one()

    if not tenant.stripe_customer_id:
        raise StripeError("No Stripe customer found. Subscribe to a plan first.")

    try:
        url = await stripe.create_billing_portal_session(
            tenant.stripe_customer_id, return_url="http://localhost:3000/settings"
        )
    except Exception as exc:
        raise StripeError(f"Failed to create portal session: {exc}") from exc

    return {"portal_url": url}


@router.get("/current", response_model=CurrentPlanResponse)
async def current_plan(user: CurrentUser, db: DBSession) -> CurrentPlanResponse:
    """Return the current subscription plan for the tenant."""
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one()

    # Check for active subscription
    sub_result = await db.execute(select(Subscription).where(Subscription.tenant_id == tenant.id))
    sub = sub_result.scalar_one_or_none()

    if sub:
        return CurrentPlanResponse(
            plan=tenant.plan.value,
            status=sub.status.value if hasattr(sub.status, "value") else str(sub.status),
            current_period_end=sub.current_period_end,
        )

    return CurrentPlanResponse(plan=tenant.plan.value, status="active")
