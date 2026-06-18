from fastapi import APIRouter

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/search")
async def search_rag(query: str):
    return {"query": query, "results": []}


@router.post("/ingest")
async def ingest_document(filename: str, content: str):
    return {"status": "success", "filename": filename}


@router.post("/query")
async def query_rag_endpoint(question: str):
    return {"answer": "Generated answer from retrieved context", "sources": []}
