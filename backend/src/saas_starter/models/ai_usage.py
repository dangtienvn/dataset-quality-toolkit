"""AI usage tracking model (ADR-004)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.saas_starter.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from backend.src.saas_starter.models.tenant import Tenant
    from backend.src.saas_starter.models.user import User


class AIUsage(TimestampMixin, Base):
    """Tracks every LLM call for billing and dashboard (ADR-004)."""

    __tablename__ = "ai_usages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=6), nullable=False, default=Decimal("0")
    )
    feature: Mapped[str] = mapped_column(String(100), nullable=False)

    tenant: Mapped[Tenant] = relationship(back_populates="ai_usages")
    user: Mapped[User] = relationship(back_populates="ai_usages")
