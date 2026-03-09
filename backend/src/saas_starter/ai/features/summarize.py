"""Summarize feature: condense text into a summary."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.saas_starter.ai.base import LLMResponse
from backend.src.saas_starter.ai.router import LLMRouter
from backend.src.saas_starter.services.usage_service import track_usage

_SYSTEM_PROMPTS = {
    "concise": "Summarize the following text concisely in 2-3 sentences.",
    "detailed": "Provide a detailed summary of the following text, preserving key points.",
    "bullet": "Summarize the following text as bullet points.",
}


class SummarizeFeature:
    """Text summarization with usage tracking."""

    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def summarize(
        self,
        text: str,
        style: str,
        model: str,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> LLMResponse:
        """Summarize text using the specified style."""
        system_prompt = _SYSTEM_PROMPTS.get(style, _SYSTEM_PROMPTS["concise"])
        response = await self.router.route(prompt=text, system_prompt=system_prompt, model=model)

        await track_usage(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            feature="summarize",
        )
        return response
