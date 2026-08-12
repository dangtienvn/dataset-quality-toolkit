def reciprocal_rank_fusion(dense_ranks: list, sparse_ranks: list, k: int = 60):
    """RRF algorithm to combine dense and sparse search results."""
    scores = {}
    for rank, doc in enumerate(dense_ranks):
        scores[doc] = scores.get(doc, 0.0) + (1.0 / (k + rank + 1))
    for rank, doc in enumerate(sparse_ranks):
        scores[doc] = scores.get(doc, 0.0) + (1.0 / (k + rank + 1))
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in sorted_docs]

# Updated audit checkpoint 2026-08-12 14:15
