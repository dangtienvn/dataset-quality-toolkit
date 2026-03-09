"""Integration tests for GDPR API endpoints."""

from httpx import AsyncClient

from backend.src.saas_starter.models.audit_log import AuditLog
from tests.conftest import TestSessionLocal, seed_tenant_and_user


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_export_tenant_data(client: AsyncClient) -> None:
    """GET /gdpr/export returns tenant data."""
    _t, _u, token = await seed_tenant_and_user(email="gdpr-exp@test.com", tenant_slug="gdpr-exp")
    resp = await client.get("/api/v1/gdpr/export", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert body["data"]["tenant"]["slug"] == "gdpr-exp"
    assert len(body["data"]["users"]) == 1


async def test_export_user_data(client: AsyncClient) -> None:
    """GET /gdpr/user/export returns user data."""
    _t, _u, token = await seed_tenant_and_user(email="gdpr-uexp@test.com", tenant_slug="gdpr-uexp")
    resp = await client.get("/api/v1/gdpr/user/export", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["user"]["email"] == "gdpr-uexp@test.com"


async def test_anonymize_logs_requires_auth(client: AsyncClient) -> None:
    """POST /gdpr/anonymize-logs without token returns 401/422."""
    resp = await client.post("/api/v1/gdpr/anonymize-logs")
    assert resp.status_code in (401, 422)


async def test_admin_dashboard(client: AsyncClient) -> None:
    """GET /admin/dashboard returns tenant stats."""
    _t, _u, token = await seed_tenant_and_user(
        email="admin-dash@test.com", tenant_slug="admin-dash"
    )
    resp = await client.get("/api/v1/admin/dashboard", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["tenant"]["plan"] == "free"
    assert body["users"]["total"] == 1
    assert body["subscription"]["status"] == "none"


async def test_delete_tenant_data_removes_records(client: AsyncClient) -> None:
    """DELETE /gdpr/tenant deletes all tenant data."""
    _t, _u, token = await seed_tenant_and_user(email="gdpr-del@test.com", tenant_slug="gdpr-del")
    resp = await client.delete("/api/v1/gdpr/tenant", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["deleted_records"] >= 1
    assert "deleted" in body["message"].lower()


async def test_delete_user_data_removes_user(client: AsyncClient) -> None:
    """DELETE /gdpr/user deletes user data."""
    _t, _u, token = await seed_tenant_and_user(email="gdpr-udel@test.com", tenant_slug="gdpr-udel")
    resp = await client.delete("/api/v1/gdpr/user", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["deleted_records"] >= 1


async def test_anonymize_logs_with_seeded_data(client: AsyncClient) -> None:
    """POST /gdpr/anonymize-logs anonymizes audit log PII."""
    _t, _u, token = await seed_tenant_and_user(email="gdpr-anon@test.com", tenant_slug="gdpr-anon")

    # Seed an audit log
    async with TestSessionLocal() as db:
        log = AuditLog(
            tenant_id=_t.id,
            user_id=_u.id,
            action="test_action",
            resource="test_resource",
            details={"key": "value"},
            ip_address="10.0.0.1",
        )
        db.add(log)
        await db.commit()

    resp = await client.post("/api/v1/gdpr/anonymize-logs", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["anonymized_records"] >= 1
