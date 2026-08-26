from saas_starter.rag.vectorstore.base import BaseVectorStore

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self.store = []

# Updated audit checkpoint 2026-08-26 14:15
