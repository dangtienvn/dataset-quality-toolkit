"""User management endpoints (tenant-scoped)."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from backend.src.saas_starter.api.deps import CurrentUser, DBSession, require_role
from backend.src.saas_starter.core.exceptions import UnauthorizedError, UserNotFoundError
from backend.src.saas_starter.core.security import hash_password
from backend.src.saas_starter.models.user import User, UserRole
from backend.src.saas_starter.schemas.auth import UserResponse
from backend.src.saas_starter.schemas.user import (
    InviteUserRequest,
    UpdateUserRequest,
    UserListResponse,
)

router = APIRouter(prefix="/users", tags=["users"])

OwnerUser = Annotated[User, Depends(require_role([UserRole.OWNER]))]


@router.get("", response_model=UserListResponse)
async def list_users(user: CurrentUser, db: DBSession) -> UserListResponse:
    """List users in the current tenant (admin+ only)."""
    if user.role not in (UserRole.OWNER, UserRole.ADMIN):
        raise UnauthorizedError("Admin or owner role required")

    query = select(User).where(User.tenant_id == user.tenant_id)
    result = await db.execute(query)
    users = list(result.scalars().all())

    count_result = await db.execute(
        select(func.count()).select_from(User).where(User.tenant_id == user.tenant_id)
    )
    total = count_result.scalar_one()

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
    )


@router.post("/invite", response_model=UserResponse, status_code=201)
async def invite_user(req: InviteUserRequest, owner: OwnerUser, db: DBSession) -> UserResponse:
    """Invite a new user into the tenant (owner only)."""
    new_user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        tenant_id=owner.tenant_id,
    )
    db.add(new_user)
    await db.flush()
    return UserResponse.model_validate(new_user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    req: UpdateUserRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> UserResponse:
    """Update a user's role or active status (admin+ only)."""
    if current_user.role not in (UserRole.OWNER, UserRole.ADMIN):
        raise UnauthorizedError("Admin or owner role required")

    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == current_user.tenant_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise UserNotFoundError(f"User {user_id} not found in your tenant")

    if req.role is not None:
        target.role = req.role
    if req.is_active is not None:
        target.is_active = req.is_active

    await db.flush()
    return UserResponse.model_validate(target)


@router.delete("/{user_id}")
async def deactivate_user(user_id: uuid.UUID, owner: OwnerUser, db: DBSession) -> dict:
    """Soft-delete a user by deactivating (owner only)."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == owner.tenant_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise UserNotFoundError(f"User {user_id} not found in your tenant")

    target.is_active = False
    await db.flush()
    return {"message": "deactivated"}
