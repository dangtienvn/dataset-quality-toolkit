"""Authentication and registration business logic."""

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.saas_starter.core.exceptions import UnauthorizedError
from backend.src.saas_starter.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from backend.src.saas_starter.models.tenant import Tenant
from backend.src.saas_starter.models.user import User, UserRole
from backend.src.saas_starter.schemas.auth import RegisterRequest, TokenResponse

# In-memory token blacklist (replaced by Redis in production)
_refresh_token_blacklist: set[str] = set()


def _slugify(name: str) -> str:
    """Convert a tenant name to a URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"[\s_-]+", "-", slug).strip("-")


def _build_token_response(user_id: str) -> TokenResponse:
    """Create access + refresh token pair for a user."""
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


async def register(db: AsyncSession, req: RegisterRequest) -> TokenResponse:
    """Create a new tenant and owner user, return JWT tokens."""
    tenant = Tenant(name=req.tenant_name, slug=_slugify(req.tenant_name))
    db.add(tenant)
    await db.flush()

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=UserRole.OWNER,
        tenant_id=tenant.id,
    )
    db.add(user)
    await db.flush()

    return _build_token_response(str(user.id))


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    """Verify credentials and return JWT tokens."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedError("User account is deactivated")

    return _build_token_response(str(user.id))


def refresh(refresh_token: str) -> TokenResponse:
    """Decode a refresh token and return a new access token."""
    if refresh_token in _refresh_token_blacklist:
        raise UnauthorizedError("Token has been revoked")

    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Not a refresh token")

    user_id = payload["sub"]
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=refresh_token,
    )


def logout(refresh_token: str) -> None:
    """Add a refresh token to the blacklist."""
    _refresh_token_blacklist.add(refresh_token)
