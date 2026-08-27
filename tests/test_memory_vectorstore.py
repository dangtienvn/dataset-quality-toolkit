import pytest
from saas_starter.rag.vectorstore.memory import InMemoryVectorStore

@pytest.mark.asyncio
async def test_in_memory_store():
    s = InMemoryVectorStore()
    assert s.store == []

# Updated audit checkpoint 2026-08-27 09:30
