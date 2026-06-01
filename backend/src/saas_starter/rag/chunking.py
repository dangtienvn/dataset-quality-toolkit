class BaseChunker:
    """Abstract base class for document chunkers."""
    def chunk(self, text: str):
        raise NotImplementedError
