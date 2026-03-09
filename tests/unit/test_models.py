"""Unit tests for SQLAlchemy models using SQLite in-memory."""

import uuid

import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from backend.src.saas_starter.models.base import Base
from backend.src.saas_starter.models.tenant import PlanType, Tenant
from backend.src.saas_starter.models.user import User, UserRole


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite database and yield a session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


def _make_tenant(slug: str = "acme-corp") -> Tenant:
    """Helper to create a Tenant instance."""
    return Tenant(
        id=uuid.uuid4(),
        name="Acme Corp",
        slug=slug,
        plan=PlanType.FREE,
        is_active=True,
    )


def test_tenant_slug_is_unique(db_session: Session) -> None:
    """Tenant.slug has a unique constraint at the schema level."""
    inspector = inspect(db_session.bind)
    unique_constraints = inspector.get_unique_constraints("tenants")
    index_info = inspector.get_indexes("tenants")

    unique_columns = set()
    for uc in unique_constraints:
        for col in uc["column_names"]:
            unique_columns.add(col)
    for idx in index_info:
        if idx.get("unique"):
            for col in idx["column_names"]:
                unique_columns.add(col)

    assert "slug" in unique_columns, "Tenant.slug must have a unique constraint"


def test_user_belongs_to_tenant(db_session: Session) -> None:
    """User.tenant_id correctly references a Tenant."""
    tenant = _make_tenant()
    db_session.add(tenant)
    db_session.flush()

    user = User(
        id=uuid.uuid4(),
        email="user@acme.com",
        hashed_password="hashed",
        full_name="Test User",
        role=UserRole.MEMBER,
        tenant_id=tenant.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    loaded = db_session.execute(select(User).where(User.id == user.id)).scalar_one()
    assert loaded.tenant_id == tenant.id
