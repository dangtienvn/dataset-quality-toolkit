from saas_starter.rag.vectorstore.base import BaseVectorStore

class ChromaVectorStore(BaseVectorStore):
    def __init__(self, path: str = "./chroma_db"):
        self.path = path

# Updated audit checkpoint 2026-08-26 09:30
