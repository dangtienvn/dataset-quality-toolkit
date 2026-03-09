"""Analyze feature: document/text analysis."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.saas_starter.ai.base import LLMResponse
from backend.src.saas_starter.ai.router import LLMRouter
from backend.src.saas_starter.services.usage_service import track_usage

_SYSTEM_PROMPTS = {
    "general": "Analyze the following text and provide key insights.",
    "sentiment": (
        "Analyze the sentiment of the following text. "
        "Classify as positive, negative, or neutral and explain."
    ),
    "entities": (
        "Extract all named entities (people, organizations, locations, dates) "
        "from the following text."
    ),
}


class AnalyzeFeature:
    """Text analysis with usage tracking."""

    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def analyze(
        self,
        text: str,
        analysis_type: str,
        model: str,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> LLMResponse:
        """Analyze text using the specified analysis type."""
        system_prompt = _SYSTEM_PROMPTS.get(analysis_type, _SYSTEM_PROMPTS["general"])
        response = await self.router.route(prompt=text, system_prompt=system_prompt, model=model)

        await track_usage(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            feature="analyze",
        )
        return response
