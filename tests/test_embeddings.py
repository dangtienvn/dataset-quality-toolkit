import pytest
from saas_starter.rag.embeddings import OpenAIEmbeddingProvider

@pytest.mark.asyncio
async def test_openai_embedding():
    provider = OpenAIEmbeddingProvider()
    vec = await provider.embed_query("test query")
    assert len(vec) == 1536

# Updated audit checkpoint 2026-08-11 14:15
