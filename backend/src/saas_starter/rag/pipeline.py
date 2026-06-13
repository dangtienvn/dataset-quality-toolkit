class RAGPipeline:
    def __init__(self, chunker, embedder, vector_store):
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    async def run(self, document_text: str):
        chunks = self.chunker.chunk(document_text)
        embeddings = await self.embedder.embed_documents(chunks)
        return await self.vector_store.add_texts(chunks, [{"source": "rag"} for _ in chunks])
