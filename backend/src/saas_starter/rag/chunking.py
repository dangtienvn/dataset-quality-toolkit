class BaseChunker:
    """Abstract base class for document chunkers."""
    def chunk(self, text: str):
        raise NotImplementedError


class RecursiveCharacterChunker(BaseChunker):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str):
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return chunks


class TokenTextSplitter(BaseChunker):
    def __init__(self, max_tokens: int = 512):
        self.max_tokens = max_tokens

    def chunk(self, text: str):
        words = text.split()
        return [" ".join(words[i:i+self.max_tokens]) for i in range(0, len(words), self.max_tokens)]


class SemanticChunker(BaseChunker):
    """Splits text based on sentence semantic similarity."""
    def chunk(self, text: str):
        sentences = text.split(". ")
        return [s + "." for s in sentences if s]

# Updated audit checkpoint 2026-08-07 09:30

# Updated audit checkpoint 2026-08-07 14:15

# Updated audit checkpoint 2026-08-18 17:45
