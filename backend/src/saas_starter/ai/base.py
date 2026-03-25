"""Base classes for the LLM abstraction layer (ADR-002)."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class LLMResponse:
    """Unified response from any LLM provider."""

    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    latency_ms: int = 0


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return a short identifier for this provider (e.g. 'openai')."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a completion from the LLM."""

    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Stream completion tokens. Default falls back to non-streaming."""
        response = await self.complete(prompt, system_prompt, model, max_tokens)
        yield response.content

    def get_cost(self, model: str, input_tokens: int, output_tokens: int) -> Decimal:
        """Estimate cost in USD for a given token count. Override per provider."""
        return Decimal("0")
