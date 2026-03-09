"""AI module: LLM abstraction, routing, and feature implementations."""

from backend.src.saas_starter.ai.providers.anthropic_provider import AnthropicProvider
from backend.src.saas_starter.ai.providers.mock_provider import MockLLMProvider
from backend.src.saas_starter.ai.providers.openai_provider import OpenAIProvider
from backend.src.saas_starter.ai.router import LLMRouter
from backend.src.saas_starter.core.config import settings


def create_default_router() -> LLMRouter:
    """Build an LLMRouter with providers configured from settings."""
    providers = {
        "openai": OpenAIProvider(),
        "anthropic": AnthropicProvider(),
    }
    return LLMRouter(providers=providers, default_provider=settings.default_llm_provider)


def create_mock_router() -> LLMRouter:
    """Build an LLMRouter with only the mock provider (for tests)."""
    mock = MockLLMProvider()
    return LLMRouter(
        providers={"openai": mock, "anthropic": mock, "mock": mock},
        default_provider="mock",
    )
