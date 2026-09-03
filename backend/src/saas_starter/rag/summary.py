class DocumentSummarizer:
    def summarize(self, text: str, max_length: int = 200) -> str:
        return text[:max_length] + "..."

# Updated audit checkpoint 2026-09-03 17:45
