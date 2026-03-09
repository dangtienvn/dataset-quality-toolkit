"""Auth request/response schemas."""

import uuid

from pydantic import BaseModel, EmailStr

from backend.src.saas_starter.models.user import UserRole


class RegisterRequest(BaseModel):
    """Registration payload: creates a new tenant and owner user."""

    email: EmailStr
    password: str
    full_name: str
    tenant_name: str


class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Token refresh payload."""

    refresh_token: str


class TokenResponse(BaseModel):
    """JWT token pair returned on login/register."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user representation."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    tenant_id: uuid.UUID
    is_active: bool
