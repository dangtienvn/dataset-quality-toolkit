"""FastAPI dependencies for auth and tenant resolution."""

import uuid as _uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.saas_starter.core.database import get_db
from backend.src.saas_starter.core.exceptions import UnauthorizedError, UserNotFoundError
from backend.src.saas_starter.core.security import decode_token
from backend.src.saas_starter.models.tenant import Tenant
from backend.src.saas_starter.models.user import User, UserRole

DBSession = Annotated[AsyncSession, Depends(get_db)]
AuthHeader = Annotated[str, Header(description="Bearer <token>")]


async def get_current_user(
    authorization: AuthHeader,
    db: DBSession,
) -> User:
    """Decode JWT from Authorization header and return the authenticated user."""
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("Authorization header must start with 'Bearer '")

    token = authorization.removeprefix("Bearer ")
    payload = decode_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Token missing 'sub' claim")

    try:
        user_id = _uuid.UUID(user_id_str)
    except ValueError as exc:
        raise UnauthorizedError(f"Invalid user id in token: {exc}") from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    if not user.is_active:
        raise UnauthorizedError("User account is deactivated")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_tenant(
    user: CurrentUser,
    db: DBSession,
) -> Tenant:
    """Resolve the tenant from the authenticated user."""
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise UnauthorizedError("Tenant not found for user")
    return tenant


def require_role(allowed_roles: list[UserRole]) -> Callable:
    """Dependency factory that restricts access to specific roles."""

    async def check_role(user: CurrentUser) -> User:
        if user.role not in allowed_roles:
            raise UnauthorizedError(
                f"Role '{user.role.value}' not in allowed roles: {[r.value for r in allowed_roles]}"
            )
        return user

    return check_role
