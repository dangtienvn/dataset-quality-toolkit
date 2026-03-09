"""Tenant model for multi-tenancy support."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.saas_starter.models.base import Base, TimestampMixin, generate_uuid


class PlanType(enum.StrEnum):
    """Subscription plan types."""

    FREE = "free"
    STARTER = "starter"
    PRO = "pro"


class Tenant(TimestampMixin, Base):
    """Organization/tenant model for row-level multi-tenancy (ADR-003)."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    plan: Mapped[PlanType] = mapped_column(Enum(PlanType), nullable=False, default=PlanType.FREE)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")  # noqa: F821
    subscriptions: Mapped[list["Subscription"]] = relationship(  # noqa: F821
        back_populates="tenant"
    )
    ai_usages: Mapped[list["AIUsage"]] = relationship(back_populates="tenant")  # noqa: F821
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="tenant")  # noqa: F821
