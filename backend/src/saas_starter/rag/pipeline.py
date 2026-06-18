class RAGPipeline:
    def __init__(self, chunker, embedder, vector_store):
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    async def run(self, document_text: str):
        chunks = self.chunker.chunk(document_text)
        embeddings = await self.embedder.embed_documents(chunks)
        return await self.vector_store.add_texts(chunks, [{"source": "rag"} for _ in chunks])


    async def query(self, question: str, top_k: int = 5):
        docs = await self.vector_store.similarity_search(question, k=top_k)
        context = "\n\n".join([d["content"] for d in docs])
        return {"context": context, "question": question}
