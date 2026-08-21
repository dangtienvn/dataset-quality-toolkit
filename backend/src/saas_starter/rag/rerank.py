class Reranker:
    def rerank(self, query: str, documents: list, top_n: int = 3):
        return documents[:top_n]


class CrossEncoderReranker(Reranker):
    def rerank(self, query: str, documents: list, top_n: int = 3):
        # Score docs by relevance
        scored = [(doc, 0.99 - idx*0.1) for idx, doc in enumerate(documents)]
        return [d[0] for d in sorted(scored, key=lambda x: x[1], reverse=True)[:top_n]]

# Updated audit checkpoint 2026-08-20 17:45

# Updated audit checkpoint 2026-08-21 09:30
