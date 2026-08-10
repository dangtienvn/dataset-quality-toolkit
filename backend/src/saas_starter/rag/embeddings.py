from typing import List

class EmbeddingProvider:
    """Abstract embedding provider."""
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    async def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Mock vector generator for embeddings
        return [[0.1 * i] * 1536 for i in range(len(texts))]

    async def embed_query(self, text: str) -> List[float]:
        return [0.1] * 1536

# Updated audit checkpoint 2026-08-08 17:45

# Updated audit checkpoint 2026-08-10 09:30
