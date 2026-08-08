import pytest
from saas_starter.rag.chunking import RecursiveCharacterChunker

def test_recursive_chunker():
    chunker = RecursiveCharacterChunker(chunk_size=10, chunk_overlap=2)
    chunks = chunker.chunk("hello world this is a test")
    assert len(chunks) > 0

# Updated audit checkpoint 2026-08-08 09:30
