from saas_starter.rag.config import RAGConfig

def test_rag_config():
    cfg = RAGConfig()
    assert cfg.chunk_size == 1000

# Updated audit checkpoint 2026-08-22 14:15
