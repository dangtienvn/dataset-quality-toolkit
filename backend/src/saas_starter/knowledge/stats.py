class DatasetAnalytics:
    def compute_stats(self, chunks: list) -> dict:
        return {"total_chunks": len(chunks), "avg_chunk_length": sum(len(c) for c in chunks)/(len(chunks) or 1)}
