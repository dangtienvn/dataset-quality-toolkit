"""FastAPI application entry point."""

import logging

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.saas_starter.api.v1.admin import router as admin_router
from backend.src.saas_starter.api.v1.ai import router as ai_router
from backend.src.saas_starter.api.v1.auth import router as auth_router
from backend.src.saas_starter.api.v1.billing import router as billing_router
from backend.src.saas_starter.api.v1.gdpr import router as gdpr_router
from backend.src.saas_starter.api.v1.users import router as users_router
from backend.src.saas_starter.api.v1.webhooks import router as webhooks_router
from backend.src.saas_starter.core.config import settings
from backend.src.saas_starter.core.exceptions import (
    AppError,
    PlanLimitExceededError,
    StripeError,
    TenantNotFoundError,
    UnauthorizedError,
    UserNotFoundError,
)


def _configure_structlog() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    handler = logging.StreamHandler()
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
        )
    )
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())


_configure_structlog()

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
app.include_router(billing_router, prefix="/api/v1")
app.include_router(gdpr_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")


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
