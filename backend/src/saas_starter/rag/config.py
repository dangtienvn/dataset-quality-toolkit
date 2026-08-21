from pydantic import BaseModel

class RAGConfig(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    similarity_threshold: float = 0.7

# Updated audit checkpoint 2026-08-21 14:15
