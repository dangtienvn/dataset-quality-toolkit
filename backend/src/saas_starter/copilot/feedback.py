class FeedbackCollector:
    def record_feedback(self, message_id: str, rating: int, comment: str = None):
        return {"message_id": message_id, "rating": rating, "comment": comment}
