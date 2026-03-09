"""Billing request/response schemas."""

from datetime import datetime

from pydantic import BaseModel


class PlanInfo(BaseModel):
    """Public plan information."""

    name: str
    price_usd: float
    features: list[str]
    price_id: str


class SubscribeRequest(BaseModel):
    """Subscription creation request."""

    price_id: str


class SubscribeResponse(BaseModel):
    """Subscription creation response."""

    checkout_url: str


class CurrentPlanResponse(BaseModel):
    """Current subscription status."""

    plan: str
    status: str
    current_period_end: datetime | None = None
