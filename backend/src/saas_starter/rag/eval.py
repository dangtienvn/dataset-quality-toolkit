class RAGEvaluator:
    """Evaluate retrieval precision and recall metrics."""
    def evaluate_recall(self, retrieved_ids: list, ground_truth_ids: list) -> float:
        if not ground_truth_ids:
            return 0.0
        hits = len(set(retrieved_ids).intersection(set(ground_truth_ids)))
        return hits / len(ground_truth_ids)


    def evaluate_precision(self, retrieved_ids: list, ground_truth_ids: list) -> float:
        if not retrieved_ids:
            return 0.0
        hits = len(set(retrieved_ids).intersection(set(ground_truth_ids)))
        return hits / len(retrieved_ids)

# Updated audit checkpoint 2026-08-29 14:15

# Updated audit checkpoint 2026-08-29 17:45
