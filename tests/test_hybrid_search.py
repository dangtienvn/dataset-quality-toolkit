from saas_starter.rag.hybrid_search import reciprocal_rank_fusion

def test_rrf():
    dense = ["doc1", "doc2", "doc3"]
    sparse = ["doc2", "doc4", "doc1"]
    results = reciprocal_rank_fusion(dense, sparse)
    assert results[0] == "doc2"
