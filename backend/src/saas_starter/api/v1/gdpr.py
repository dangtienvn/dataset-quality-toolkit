"""GDPR compliance endpoints: export, delete, anonymize."""

from fastapi import APIRouter

from backend.src.saas_starter.api.deps import CurrentUser, DBSession
from backend.src.saas_starter.schemas.gdpr import (
    AnonymizeResponse,
    DeletionResponse,
    ExportResponse,
)
from backend.src.saas_starter.services.gdpr_service import GDPRService

router = APIRouter(prefix="/gdpr", tags=["gdpr"])


@router.get("/export", response_model=ExportResponse)
async def export_tenant_data(user: CurrentUser, db: DBSession) -> ExportResponse:
    """Export all data for the current tenant (GDPR Art. 20)."""
    svc = GDPRService(db)
    data = await svc.export_tenant_data(user.tenant_id)
    return ExportResponse(data=data)


@router.delete("/tenant", response_model=DeletionResponse)
async def delete_tenant_data(user: CurrentUser, db: DBSession) -> DeletionResponse:
    """Delete all data for the current tenant (GDPR Art. 17)."""
    svc = GDPRService(db)
    count = await svc.delete_tenant_data(user.tenant_id)
    return DeletionResponse(deleted_records=count, message="Tenant data deleted successfully")


@router.get("/user/export", response_model=ExportResponse)
async def export_user_data(user: CurrentUser, db: DBSession) -> ExportResponse:
    """Export all data for the current user (GDPR Art. 20)."""
    svc = GDPRService(db)
    data = await svc.export_user_data(user.id)
    return ExportResponse(data=data)


@router.delete("/user", response_model=DeletionResponse)
async def delete_user_data(user: CurrentUser, db: DBSession) -> DeletionResponse:
    """Delete all data for the current user (GDPR Art. 17)."""
    svc = GDPRService(db)
    count = await svc.delete_user(user.id)
    return DeletionResponse(deleted_records=count, message="User data deleted successfully")


@router.post("/anonymize-logs", response_model=AnonymizeResponse)
async def anonymize_logs(user: CurrentUser, db: DBSession) -> AnonymizeResponse:
    """Anonymize audit logs for the current tenant."""
    svc = GDPRService(db)
    count = await svc.anonymize_logs(user.tenant_id)
    return AnonymizeResponse(anonymized_records=count, message="Audit logs anonymized successfully")
