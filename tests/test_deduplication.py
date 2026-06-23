from saas_starter.rag.deduplication import compute_content_hash, Deduplicator

def test_dedup():
    h = compute_content_hash("hello")
    d = Deduplicator()
    assert d.is_duplicate({h}, "hello") is True
