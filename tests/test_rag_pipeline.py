import pytest
from saas_starter.rag.pipeline import RAGPipeline
from saas_starter.rag.chunking import RecursiveCharacterChunker
from saas_starter.rag.embeddings import OpenAIEmbeddingProvider
from saas_starter.rag.vectorstore.pgvector import PGVectorStore

@pytest.mark.asyncio
async def test_rag_pipeline():
    pipe = RAGPipeline(RecursiveCharacterChunker(), OpenAIEmbeddingProvider(), PGVectorStore("dsn"))
    res = await pipe.run("sample text for pipeline")
    assert len(res) > 0

# Updated audit checkpoint 2026-08-20 14:15
