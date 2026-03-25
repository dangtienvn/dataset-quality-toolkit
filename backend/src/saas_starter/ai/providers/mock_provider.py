"""Mock LLM provider for testing — no real HTTP calls."""

from decimal import Decimal

from backend.src.saas_starter.ai.base import BaseLLMProvider, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock provider that returns fixed responses."""

    @property
    def provider_name(self) -> str:
        return "mock"

    async def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Return a fixed response without any HTTP calls."""
        return LLMResponse(
            content=f"Mock response to: {prompt[:50]}",
            model=model or "mock-model",
            provider=self.provider_name,
            input_tokens=10,
            output_tokens=20,
            cost_usd=Decimal("0.001"),
        )
