"""GDPR request/response schemas."""

from pydantic import BaseModel


class ExportResponse(BaseModel):
    """Response for data export requests."""

    data: dict


class DeletionResponse(BaseModel):
    """Response for data deletion requests."""

    deleted_records: int
    message: str


class AnonymizeResponse(BaseModel):
    """Response for log anonymization requests."""

    anonymized_records: int
    message: str
