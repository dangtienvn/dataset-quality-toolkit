"""AI usage tracking service (ADR-004)."""

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.saas_starter.models.ai_usage import AIUsage


async def track_usage(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: Decimal,
    feature: str,
) -> AIUsage:
    """Record a single LLM call in the usage table."""
    record = AIUsage(
        tenant_id=tenant_id,
        user_id=user_id,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
        feature=feature,
    )
    db.add(record)
    await db.flush()
    return record


async def get_usage_summary(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    days: int = 30,
) -> dict:
    """Aggregate usage stats for a tenant over the given period."""
    cutoff = func.datetime("now", f"-{days} days")

    query = (
        select(
            func.coalesce(func.sum(AIUsage.input_tokens + AIUsage.output_tokens), 0).label(
                "total_tokens"
            ),
            func.coalesce(func.sum(AIUsage.cost_usd), Decimal("0")).label("total_cost"),
            func.count(AIUsage.id).label("calls_count"),
        )
        .where(AIUsage.tenant_id == tenant_id)
        .where(AIUsage.created_at >= cutoff)
    )

    result = await db.execute(query)
    row = result.one()

    return {
        "total_tokens": int(row.total_tokens),
        "total_cost": str(row.total_cost),
        "calls_count": int(row.calls_count),
        "period_days": days,
    }
