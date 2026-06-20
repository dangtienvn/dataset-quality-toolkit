from saas_starter.rag.vectorstore.base import BaseVectorStore

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self.store = []
