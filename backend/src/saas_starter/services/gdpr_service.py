"""GDPR compliance service — data export, deletion, anonymization."""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.saas_starter.models.ai_usage import AIUsage
from backend.src.saas_starter.models.audit_log import AuditLog
from backend.src.saas_starter.models.subscription import Subscription
from backend.src.saas_starter.models.tenant import Tenant
from backend.src.saas_starter.models.user import User


class GDPRService:
    """Handles GDPR data export, deletion, and anonymization."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def export_tenant_data(self, tenant_id: uuid.UUID) -> dict:
        """Export all data belonging to a tenant."""
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            return {"tenant": None, "users": [], "ai_usages": [], "audit_logs": []}

        users_result = await self.db.execute(select(User).where(User.tenant_id == tenant_id))
        users = users_result.scalars().all()

        usages_result = await self.db.execute(select(AIUsage).where(AIUsage.tenant_id == tenant_id))
        usages = usages_result.scalars().all()

        logs_result = await self.db.execute(select(AuditLog).where(AuditLog.tenant_id == tenant_id))
        logs = logs_result.scalars().all()

        return {
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name,
                "slug": tenant.slug,
                "plan": tenant.plan.value,
            },
            "users": [
                {
                    "id": str(u.id),
                    "email": u.email,
                    "full_name": u.full_name,
                    "role": u.role.value,
                }
                for u in users
            ],
            "ai_usages": [
                {
                    "id": str(u.id),
                    "model": u.model,
                    "input_tokens": u.input_tokens,
                    "output_tokens": u.output_tokens,
                    "cost_usd": str(u.cost_usd),
                    "feature": u.feature,
                }
                for u in usages
            ],
            "audit_logs": [
                {
                    "id": str(log.id),
                    "action": log.action,
                    "resource": log.resource,
                    "details": log.details,
                    "ip_address": log.ip_address,
                }
                for log in logs
            ],
        }

    async def delete_tenant_data(self, tenant_id: uuid.UUID) -> int:
        """Delete all data belonging to a tenant. Returns count of deleted records."""
        deleted = 0

        # Delete audit logs
        logs = await self.db.execute(select(AuditLog).where(AuditLog.tenant_id == tenant_id))
        for log in logs.scalars().all():
            await self.db.delete(log)
            deleted += 1

        # Delete AI usages
        usages = await self.db.execute(select(AIUsage).where(AIUsage.tenant_id == tenant_id))
        for usage in usages.scalars().all():
            await self.db.delete(usage)
            deleted += 1

        # Delete subscriptions
        subs = await self.db.execute(
            select(Subscription).where(Subscription.tenant_id == tenant_id)
        )
        for sub in subs.scalars().all():
            await self.db.delete(sub)
            deleted += 1

        # Delete users
        users = await self.db.execute(select(User).where(User.tenant_id == tenant_id))
        for user in users.scalars().all():
            await self.db.delete(user)
            deleted += 1

        # Delete tenant
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if tenant:
            await self.db.delete(tenant)
            deleted += 1

        await self.db.flush()
        return deleted

    async def export_user_data(self, user_id: uuid.UUID) -> dict:
        """Export all data belonging to a specific user."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"user": None, "ai_usages": [], "audit_logs": []}

        usages_result = await self.db.execute(select(AIUsage).where(AIUsage.user_id == user_id))
        usages = usages_result.scalars().all()

        logs_result = await self.db.execute(select(AuditLog).where(AuditLog.user_id == user_id))
        logs = logs_result.scalars().all()

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
            },
            "ai_usages": [
                {
                    "id": str(u.id),
                    "model": u.model,
                    "input_tokens": u.input_tokens,
                    "output_tokens": u.output_tokens,
                    "cost_usd": str(u.cost_usd),
                    "feature": u.feature,
                }
                for u in usages
            ],
            "audit_logs": [
                {
                    "id": str(log.id),
                    "action": log.action,
                    "resource": log.resource,
                    "details": log.details,
                    "ip_address": log.ip_address,
                }
                for log in logs
            ],
        }

    async def delete_user(self, user_id: uuid.UUID) -> int:
        """Delete a user and their associated data. Returns count of deleted records."""
        deleted = 0

        # Delete user's audit logs
        logs = await self.db.execute(select(AuditLog).where(AuditLog.user_id == user_id))
        for log in logs.scalars().all():
            await self.db.delete(log)
            deleted += 1

        # Delete user's AI usages
        usages = await self.db.execute(select(AIUsage).where(AIUsage.user_id == user_id))
        for usage in usages.scalars().all():
            await self.db.delete(usage)
            deleted += 1

        # Delete user
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            await self.db.delete(user)
            deleted += 1

        await self.db.flush()
        return deleted

    async def anonymize_logs(self, tenant_id: uuid.UUID) -> int:
        """Anonymize audit logs for a tenant. Returns count of anonymized records."""
        result = await self.db.execute(select(AuditLog).where(AuditLog.tenant_id == tenant_id))
        logs = result.scalars().all()
        count = len(logs)

        if count > 0:
            await self.db.execute(
                update(AuditLog)
                .where(AuditLog.tenant_id == tenant_id)
                .values(ip_address="0.0.0.0", user_id=None, details=None)
            )
            await self.db.flush()

        return count
