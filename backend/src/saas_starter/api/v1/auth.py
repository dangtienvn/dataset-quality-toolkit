"""Auth endpoints: register, login, refresh, logout, me."""

from fastapi import APIRouter

from backend.src.saas_starter.api.deps import CurrentUser, DBSession
from backend.src.saas_starter.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from backend.src.saas_starter.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: DBSession) -> TokenResponse:
    """Register a new tenant and owner user."""
    return await auth_service.register(db, req)


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(req: LoginRequest, db: DBSession) -> TokenResponse:
    """Authenticate with email and password."""
    return await auth_service.login(db, req.email, req.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_endpoint(req: RefreshRequest) -> TokenResponse:
    """Get a new access token using a refresh token."""
    return auth_service.refresh(req.refresh_token)


@router.post("/logout")
async def logout_endpoint(req: RefreshRequest) -> dict:
    """Revoke a refresh token."""
    auth_service.logout(req.refresh_token)
    return {"message": "logged out"}


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    """Return the currently authenticated user."""
    return UserResponse.model_validate(user)
