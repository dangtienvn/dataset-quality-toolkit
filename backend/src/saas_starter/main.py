"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.saas_starter.api.v1.ai import router as ai_router
from backend.src.saas_starter.api.v1.auth import router as auth_router
from backend.src.saas_starter.api.v1.users import router as users_router
from backend.src.saas_starter.core.config import settings
from backend.src.saas_starter.core.exceptions import (
    AppError,
    PlanLimitExceededError,
    StripeError,
    TenantNotFoundError,
    UnauthorizedError,
    UserNotFoundError,
)

app = FastAPI(title="ai-saas-starter", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

_STATUS_MAP: dict[type[AppError], int] = {
    UnauthorizedError: 401,
    UserNotFoundError: 404,
    TenantNotFoundError: 404,
    PlanLimitExceededError: 403,
    StripeError: 502,
}


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Map custom exceptions to HTTP status codes."""
    status = _STATUS_MAP.get(type(exc), 500)
    return JSONResponse(status_code=status, content={"detail": exc.message})


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/api/v1/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
