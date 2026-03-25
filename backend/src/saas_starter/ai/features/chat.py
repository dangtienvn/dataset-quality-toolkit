"""Chat feature: multi-turn conversation with LLM."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.saas_starter.ai.base import LLMResponse
from backend.src.saas_starter.ai.router import LLMRouter
from backend.src.saas_starter.services.usage_service import track_usage


class ChatFeature:
    """Chat completion with usage tracking."""

    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def complete(
        self,
        messages: list[dict],
        model: str,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> LLMResponse:
        """Send messages to LLM and track usage."""
        prompt = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages)
        response = await self.router.route(prompt=prompt, model=model)

        await track_usage(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            feature="chat",
            provider=response.provider,
            latency_ms=response.latency_ms,
            endpoint="/ai/chat",
        )
        return response
