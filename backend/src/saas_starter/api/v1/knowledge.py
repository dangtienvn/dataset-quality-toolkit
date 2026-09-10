from fastapi import APIRouter, Depends
from saas_starter.knowledge.service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
service = KnowledgeBaseService()

@router.post("/datasets")
async def create_dataset_endpoint(name: str):
    return service.create_dataset(name)


@router.get("/datasets")
async def list_datasets():
    return list(service.datasets.values())


@router.get("/chunks/{chunk_id}")
async def get_chunk_preview(chunk_id: str):
    return {"id": chunk_id, "content": "Sample chunk content snippet"}


@router.post("/sync/s3")
async def trigger_s3_sync(bucket: str):
    return {"message": f"Sync scheduled for bucket {bucket}"}

# Updated audit checkpoint 2026-09-10 14:15
