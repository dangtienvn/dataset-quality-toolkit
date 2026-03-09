"""Subscription model for Stripe billing (ADR-005)."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.saas_starter.models.base import Base, TimestampMixin, generate_uuid


class SubscriptionStatus(enum.StrEnum):
    """Stripe subscription statuses."""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"


class Subscription(TimestampMixin, Base):
    """Stripe subscription linked to a tenant."""

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=False)
    stripe_price_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE
    )
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="subscriptions")  # noqa: F821
