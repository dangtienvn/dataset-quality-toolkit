"""Admin dashboard endpoint."""

from fastapi import APIRouter
from sqlalchemy import func, select

from backend.src.saas_starter.api.deps import CurrentUser, DBSession
from backend.src.saas_starter.models.ai_usage import AIUsage
from backend.src.saas_starter.models.subscription import Subscription
from backend.src.saas_starter.models.tenant import Tenant
from backend.src.saas_starter.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def dashboard(user: CurrentUser, db: DBSession) -> dict:
    """Return tenant dashboard stats."""
    tenant_id = user.tenant_id

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one()

    users_count = await db.execute(
        select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
    )
    total_users = users_count.scalar() or 0

    usage_result = await db.execute(
        select(
            func.count().label("total_calls"),
            func.coalesce(func.sum(AIUsage.input_tokens), 0).label("total_input_tokens"),
            func.coalesce(func.sum(AIUsage.output_tokens), 0).label("total_output_tokens"),
            func.coalesce(func.sum(AIUsage.cost_usd), 0).label("total_cost"),
        ).where(AIUsage.tenant_id == tenant_id)
    )
    usage = usage_result.one()

    sub_result = await db.execute(select(Subscription).where(Subscription.tenant_id == tenant_id))
    sub = sub_result.scalar_one_or_none()

    return {
        "tenant": {"name": tenant.name, "plan": tenant.plan.value},
        "users": {"total": total_users},
        "ai_usage": {
            "total_calls": usage.total_calls,
            "total_input_tokens": usage.total_input_tokens,
            "total_output_tokens": usage.total_output_tokens,
            "total_cost": str(usage.total_cost),
        },
        "subscription": {
            "status": (sub.status.value if hasattr(sub.status, "value") else str(sub.status))
            if sub
            else "none",
        },
    }
