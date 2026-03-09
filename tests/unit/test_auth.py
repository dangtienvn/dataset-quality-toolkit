"""Unit tests for auth_service logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from backend.src.saas_starter.core.exceptions import UnauthorizedError
from backend.src.saas_starter.core.security import (
    create_refresh_token,
)
from backend.src.saas_starter.schemas.auth import RegisterRequest
from backend.src.saas_starter.services import auth_service
from backend.src.saas_starter.services.auth_service import (
    _refresh_token_blacklist,
    login,
    logout,
    refresh,
    register,
)


@pytest.fixture(autouse=True)
def _clear_blacklist():
    """Ensure the blacklist is empty before each test."""
    _refresh_token_blacklist.clear()
    yield
    _refresh_token_blacklist.clear()


async def test_register_creates_tenant_and_user() -> None:
    """register() adds a Tenant and a User to the session."""
    db = AsyncMock()
    added_objects: list = []
    db.add = MagicMock(side_effect=lambda obj: added_objects.append(obj))
    db.flush = AsyncMock()

    req = RegisterRequest(
        email="owner@acme.com",
        password="strongpass",
        full_name="Alice",
        tenant_name="Acme Corp",
    )

    with patch.object(auth_service, "hash_password", return_value="hashed"):
        result = await register(db, req)

    assert len(added_objects) == 2
    tenant, user = added_objects
    assert tenant.name == "Acme Corp"
    assert tenant.slug == "acme-corp"
    assert user.email == "owner@acme.com"
    assert user.role.value == "owner"
    assert result.access_token
    assert result.refresh_token


async def test_login_wrong_password_raises_unauthorized() -> None:
    """login() raises UnauthorizedError for wrong password."""
    fake_user = MagicMock()
    fake_user.hashed_password = "hashed"
    fake_user.is_active = True

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user

    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)

    with (
        patch.object(auth_service, "verify_password", return_value=False),
        pytest.raises(UnauthorizedError, match="Invalid email or password"),
    ):
        await login(db, "user@example.com", "wrongpass")


def test_refresh_token_valid() -> None:
    """refresh() returns a new access token for a valid refresh token."""
    token = create_refresh_token("user-123")
    result = refresh(token)

    assert result.access_token
    assert result.refresh_token == token


def test_logout_blacklists_token() -> None:
    """logout() adds the token to the blacklist, and refresh() rejects it."""
    token = create_refresh_token("user-123")
    logout(token)

    with pytest.raises(UnauthorizedError, match="revoked"):
        refresh(token)


async def test_register_duplicate_email_raises_error() -> None:
    """register() with duplicate email raises an error from the DB."""
    from tests.conftest import TestSessionLocal

    # First registration
    async with TestSessionLocal() as db:
        req = RegisterRequest(
            email="dup@test.com",
            password="pass123",
            full_name="First",
            tenant_name="First Co",
        )
        await register(db, req)
        await db.commit()

    # Second registration with same email should fail
    async with TestSessionLocal() as db:
        req2 = RegisterRequest(
            email="dup@test.com",
            password="pass123",
            full_name="Second",
            tenant_name="Second Co",
        )
        with pytest.raises(IntegrityError):
            await register(db, req2)
            await db.commit()


def test_refresh_blacklisted_token_raises_unauthorized() -> None:
    """refresh() rejects a token that was previously blacklisted via logout()."""
    token = create_refresh_token("user-456")

    # Token works initially
    result = refresh(token)
    assert result.access_token

    # Blacklist it
    logout(token)

    # Now it should be rejected
    with pytest.raises(UnauthorizedError, match="revoked"):
        refresh(token)


async def test_login_success_returns_tokens() -> None:
    """login() with correct credentials returns tokens."""
    import uuid

    from backend.src.saas_starter.core.security import hash_password
    from backend.src.saas_starter.models.tenant import PlanType, Tenant
    from backend.src.saas_starter.models.user import User, UserRole
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as db:
        tenant = Tenant(id=uuid.uuid4(), name="LoginCo", slug="login-co", plan=PlanType.FREE)
        db.add(tenant)
        await db.flush()

        user = User(
            id=uuid.uuid4(),
            email="loginsuccess@test.com",
            hashed_password=hash_password("correct_pass"),
            full_name="Login User",
            role=UserRole.OWNER,
            tenant_id=tenant.id,
        )
        db.add(user)
        await db.commit()

    async with TestSessionLocal() as db:
        result = await login(db, "loginsuccess@test.com", "correct_pass")

    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"
