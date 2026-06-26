class RAGException(Exception):
    """Base RAG exception."""

class VectorStoreException(RAGException):
    """Vector store operation error."""
