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
