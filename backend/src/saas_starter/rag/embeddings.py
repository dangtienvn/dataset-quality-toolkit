from typing import List

class EmbeddingProvider:
    """Abstract embedding provider."""
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    async def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError
