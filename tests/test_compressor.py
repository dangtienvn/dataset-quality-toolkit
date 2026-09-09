from saas_starter.knowledge.context_compressor import ContextWindowCompressor

def test_compressor():
    c = ContextWindowCompressor()
    res = c.compress(["chunk1", "chunk2"], 100)
    assert "chunk1" in res

# Updated audit checkpoint 2026-09-09 09:30
