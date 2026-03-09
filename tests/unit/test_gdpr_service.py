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


async def test_export_user_data_returns_user_and_usage() -> None:
    """export_user_data includes user info and associated AI usage records."""
    tenant_id, user_id = await _seed_full_tenant()

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_user_data(user_id)

    assert data["user"]["email"] == "gdpr@test.com"
    assert data["user"]["full_name"] == "GDPR User"
    assert data["user"]["role"] == "owner"
    assert len(data["ai_usages"]) == 1
    assert data["ai_usages"][0]["model"] == "mock-model"
    assert data["ai_usages"][0]["cost_usd"] == "0.001000"


async def test_anonymize_logs_returns_zero_when_no_old_logs() -> None:
    """anonymize_logs returns 0 when no logs exist for the tenant."""
    no_logs_tenant_id = uuid.uuid4()

    async with TestSessionLocal() as db:
        tenant = Tenant(id=no_logs_tenant_id, name="NoLogs", slug="nologs-test", plan=PlanType.FREE)
        db.add(tenant)
        await db.commit()

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        count = await svc.anonymize_logs(no_logs_tenant_id)

    assert count == 0


async def test_delete_user_removes_user_and_related_data() -> None:
    """delete_user removes user, their usages, and audit logs."""
    _tenant_id, user_id = await _seed_full_tenant()

    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        count = await svc.delete_user(user_id)
        await db.commit()

    # user + usage + log = 3
    assert count == 3

    # Verify user is gone
    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_user_data(user_id)
    assert data["user"] is None


async def test_export_user_data_nonexistent_returns_empty() -> None:
    """export_user_data for non-existent user returns None user."""
    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_user_data(uuid.uuid4())
    assert data["user"] is None
    assert data["ai_usages"] == []
    assert data["audit_logs"] == []


async def test_export_tenant_data_nonexistent_returns_empty() -> None:
    """export_tenant_data for non-existent tenant returns None tenant."""
    async with TestSessionLocal() as db:
        svc = GDPRService(db)
        data = await svc.export_tenant_data(uuid.uuid4())
    assert data["tenant"] is None
