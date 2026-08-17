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


    async def process_with_retry(self, texts: list, retries: int = 3):
        for attempt in range(retries):
            try:
                return await self.process_in_batches(texts)
            except Exception:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(1)

# Updated audit checkpoint 2026-08-15 17:45

# Updated audit checkpoint 2026-08-17 09:30
