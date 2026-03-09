"""Unit tests for GDPR service."""

import uuid
from decimal import Decimal

from backend.src.saas_starter.models.ai_usage import AIUsage
from backend.src.saas_starter.models.audit_log import AuditLog
from backend.src.saas_starter.models.tenant import PlanType, Tenant
from backend.src.saas_starter.models.user import User, UserRole
from backend.src.saas_starter.services.gdpr_service import GDPRService
from tests.conftest import TestSessionLocal


async def _seed_full_tenant() -> tuple[uuid.UUID, uuid.UUID]:
    """Seed a tenant with user, usage, and audit log. Return (tenant_id, user_id)."""
    async with TestSessionLocal() as db:
        tenant = Tenant(id=uuid.uuid4(), name="GDPR", slug="gdpr-test", plan=PlanType.FREE)
        db.add(tenant)
        await db.flush()

        user = User(
            id=uuid.uuid4(),
            email="gdpr@test.com",
            hashed_password="hashed",
            full_name="GDPR User",
            role=UserRole.OWNER,
            tenant_id=tenant.id,
        )
        db.add(user)
        await db.flush()

        usage = AIUsage(
            tenant_id=tenant.id,
            user_id=user.id,
            model="mock-model",
            input_tokens=10,
            output_tokens=20,
            cost_usd=Decimal("0.001"),
            feature="chat",
        )
        db.add(usage)

        log = AuditLog(
            tenant_id=tenant.id,
            user_id=user.id,
            action="login",
            resource="auth",
            details={"method": "password"},
            ip_address="192.168.1.1",
        )
        db.add(log)
        await db.commit()

        return tenant.id, user.id


async def test_export_tenant_data_returns_all_records() -> None:
    """export_tenant_data returns tenant, users, usages, and logs."""
    tenant_id, _user_id = await _seed_full_tenant()

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_tenant_data(tenant_id)

    assert data["tenant"]["id"] == str(tenant_id)
    assert len(data["users"]) == 1
    assert len(data["ai_usages"]) == 1
    assert len(data["audit_logs"]) == 1


async def test_delete_tenant_data_removes_everything() -> None:
    """delete_tenant_data removes tenant, user, usage, and log."""
    tenant_id, _user_id = await _seed_full_tenant()

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        count = await svc.delete_tenant_data(tenant_id)
        await db.commit()

    # tenant + user + usage + log = 4
    assert count == 4

    # Verify nothing remains
    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_tenant_data(tenant_id)
    assert data["tenant"] is None


async def test_export_user_data_returns_user_records() -> None:
    """export_user_data returns user info, usages, and logs."""
    _tenant_id, user_id = await _seed_full_tenant()

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_user_data(user_id)

    assert data["user"]["id"] == str(user_id)
    assert len(data["ai_usages"]) == 1
    assert len(data["audit_logs"]) == 1


async def test_anonymize_logs_clears_pii() -> None:
    """anonymize_logs sets ip_address to 0.0.0.0 and nullifies user_id and details."""
    tenant_id, _user_id = await _seed_full_tenant()

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        count = await svc.anonymize_logs(tenant_id)
        await db.commit()

    assert count == 1

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_tenant_data(tenant_id)

    log = data["audit_logs"][0]
    assert log["ip_address"] == "0.0.0.0"
    assert log["details"] is None
