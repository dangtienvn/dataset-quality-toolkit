"""Shared test fixtures: async engine, client, seed helpers.

By default tests use an in-memory SQLite database for speed.
Set TEST_DATABASE_URL to a PostgreSQL connection string to run
against a real database (used in CI).
"""

import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.saas_starter.ai import create_mock_router
from backend.src.saas_starter.api.v1.ai import get_llm_router
from backend.src.saas_starter.core.database import get_db
from backend.src.saas_starter.core.security import create_access_token, hash_password
from backend.src.saas_starter.main import app
from backend.src.saas_starter.models.base import Base
from backend.src.saas_starter.models.tenant import PlanType, Tenant
from backend.src.saas_starter.models.user import User, UserRole

# ---------------------------------------------------------------------------
# Test engine: PostgreSQL when TEST_DATABASE_URL is set, SQLite otherwise
# ---------------------------------------------------------------------------

_test_db_url = os.environ.get("TEST_DATABASE_URL", "")

if _test_db_url:
    from sqlalchemy.pool import NullPool

    test_engine = create_async_engine(_test_db_url, poolclass=NullPool)
else:
    from sqlalchemy import StaticPool, event

    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine.sync_engine, "connect")
    def _enable_fk(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


async def _override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = _override_get_db
app.dependency_overrides[get_llm_router] = create_mock_router


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


async def seed_tenant_and_user(
    role: UserRole = UserRole.OWNER,
    email: str = "seed@acme.com",
    tenant_slug: str = "acme",
    tenant_name: str = "Acme",
) -> tuple[Tenant, User, str]:
    """Seed a tenant + user and return (tenant, user, access_token)."""
    async with TestSessionLocal() as db:
        tenant = Tenant(id=uuid.uuid4(), name=tenant_name, slug=tenant_slug, plan=PlanType.FREE)
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
