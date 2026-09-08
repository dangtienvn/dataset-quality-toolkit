class ContextWindowCompressor:
    def compress(self, context_chunks: list, max_tokens: int = 2000) -> str:
        combined = "\n".join(context_chunks)
        return combined[:max_tokens * 4]

# Updated audit checkpoint 2026-09-08 17:45
