import asyncio
from typing import AsyncGenerator

class AsyncTokenStreamer:
    async def stream_tokens(self, text: str) -> AsyncGenerator[str, None]:
        words = text.split()
        for w in words:
            yield w + " "
            await asyncio.sleep(0.05)
