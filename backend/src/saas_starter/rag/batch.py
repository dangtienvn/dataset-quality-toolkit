import asyncio

class BatchEmbeddingProcessor:
    def __init__(self, provider, batch_size: int = 32):
        self.provider = provider
        self.batch_size = batch_size

    async def process_in_batches(self, texts: list):
        results = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            embeddings = await self.provider.embed_documents(batch)
            results.extend(embeddings)
        return results
