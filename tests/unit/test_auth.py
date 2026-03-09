"""Unit tests for auth_service logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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
