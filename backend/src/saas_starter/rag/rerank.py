class Reranker:
    def rerank(self, query: str, documents: list, top_n: int = 3):
        return documents[:top_n]
