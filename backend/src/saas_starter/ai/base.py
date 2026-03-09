"""Base classes for the LLM abstraction layer (ADR-002)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class LLMResponse:
    """Unified response from any LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Generate a completion from the LLM."""
