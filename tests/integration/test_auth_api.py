"""Integration tests for auth API endpoints using async SQLite in-memory."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.saas_starter.core.database import get_db
from backend.src.saas_starter.core.security import create_access_token, hash_password
from backend.src.saas_starter.main import app
from backend.src.saas_starter.models.base import Base
from backend.src.saas_starter.models.tenant import PlanType, Tenant
from backend.src.saas_starter.models.user import User, UserRole

# ---------------------------------------------------------------------------
# Async SQLite test engine
# ---------------------------------------------------------------------------

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine.sync_engine, "connect")
def _enable_fk(dbapi_conn, _connection_record):
    """Enable foreign key support in SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


async def _override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = _override_get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
async def _setup_db():
    """Create tables before each test and drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client():
    """Async HTTP client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _seed_tenant_and_user(
    role: UserRole = UserRole.OWNER,
    email: str = "seed@acme.com",
    tenant_slug: str = "acme",
) -> tuple[Tenant, User, str]:
    """Seed a tenant + user and return (tenant, user, access_token)."""
    async with TestSessionLocal() as db:
        tenant = Tenant(
            id=uuid.uuid4(), name="Acme", slug=tenant_slug, plan=PlanType.FREE
        )
        db.add(tenant)
        await db.flush()

        user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hash_password("pass123"),
            full_name="Seed User",
            role=role,
            tenant_id=tenant.id,
        )
        db.add(user)
        await db.commit()

    token = create_access_token(str(user.id))
    return tenant, user, token


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_register_returns_tokens(client: AsyncClient) -> None:
    """POST /register creates tenant+user and returns tokens."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@startup.io",
            "password": "s3cure!",
            "full_name": "New Owner",
            "tenant_name": "Startup Inc",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_returns_tokens(client: AsyncClient) -> None:
    """POST /login with valid credentials returns tokens."""
    _tenant, _user, _token = await _seed_tenant_and_user(email="login@acme.com")

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@acme.com", "password": "pass123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_me_requires_auth(client: AsyncClient) -> None:
    """GET /me without token returns 401."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 422)


async def test_refresh_works(client: AsyncClient) -> None:
    """POST /refresh returns a new access token."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@test.io",
            "password": "pass",
            "full_name": "R",
            "tenant_name": "RefreshCo",
        },
    )
    refresh_token = resp.json()["refresh_token"]

    resp2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp2.status_code == 200
    assert "access_token" in resp2.json()


async def test_tenant_isolation(client: AsyncClient) -> None:
    """User from tenant A cannot see users from tenant B."""
    _t_a, _u_a, token_a = await _seed_tenant_and_user(
        email="a@tenant-a.com", tenant_slug="tenant-a"
    )
    _t_b, _u_b, _token_b = await _seed_tenant_and_user(
        email="b@tenant-b.com", tenant_slug="tenant-b"
    )

    resp = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    emails = [u["email"] for u in body["users"]]
    assert "a@tenant-a.com" in emails
    assert "b@tenant-b.com" not in emails


async def test_invite_requires_owner_role(client: AsyncClient) -> None:
    """POST /users/invite as member returns 401."""
    _t, _u, member_token = await _seed_tenant_and_user(
        role=UserRole.MEMBER, email="member@acme.com", tenant_slug="acme-member"
    )

    resp = await client.post(
        "/api/v1/users/invite",
        headers={"Authorization": f"Bearer {member_token}"},
        json={
            "email": "invited@acme.com",
            "password": "pass",
            "full_name": "Invited",
            "role": "member",
        },
    )
    assert resp.status_code == 401
