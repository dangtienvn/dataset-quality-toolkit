import pytest
from saas_starter.copilot.streaming import AsyncTokenStreamer, SSEStreamManager

@pytest.mark.asyncio
async def test_streamer():
    streamer = AsyncTokenStreamer()
    tokens = [t async for t in streamer.stream_tokens("hello world")]
    assert len(tokens) == 2
