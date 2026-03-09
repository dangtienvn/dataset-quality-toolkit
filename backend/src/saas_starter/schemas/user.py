"""User management request/response schemas."""

from pydantic import BaseModel, EmailStr

from backend.src.saas_starter.models.user import UserRole
from backend.src.saas_starter.schemas.auth import UserResponse


class InviteUserRequest(BaseModel):
    """Invite a new user into the current tenant."""

    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.MEMBER


class UpdateUserRequest(BaseModel):
    """Partial update of a user."""

    role: UserRole | None = None
    is_active: bool | None = None


class UserListResponse(BaseModel):
    """Paginated list of users."""

    users: list[UserResponse]
    total: int
