"""Unit tests for LLM router with MockLLMProvider."""

from backend.src.saas_starter.ai.base import BaseLLMProvider, LLMResponse
from backend.src.saas_starter.ai.providers.mock_provider import MockLLMProvider
from backend.src.saas_starter.ai.router import LLMRouter


class _FailingProvider(BaseLLMProvider):
    """Provider that always raises an error."""

    async def complete(self, prompt, system_prompt="", model="", max_tokens=1024):
        raise RuntimeError("Provider unavailable")


def _make_router(
    openai: BaseLLMProvider | None = None,
    anthropic: BaseLLMProvider | None = None,
    default: str = "openai",
) -> LLMRouter:
    providers = {
        "openai": openai or MockLLMProvider(),
        "anthropic": anthropic or MockLLMProvider(),
    }
    return LLMRouter(providers=providers, default_provider=default)


async def test_routes_gpt_model_to_openai_provider() -> None:
    """Models starting with 'gpt-' route to the openai provider."""
    router = _make_router()
    provider = router.get_provider("gpt-4o-mini")
    assert provider is router.providers["openai"]


async def test_routes_claude_model_to_anthropic_provider() -> None:
    """Models starting with 'claude-' route to the anthropic provider."""
    router = _make_router()
    provider = router.get_provider("claude-sonnet-4-20250514")
    assert provider is router.providers["anthropic"]


async def test_uses_default_provider_for_unknown_model() -> None:
    """Unknown model names fall back to the default provider."""
    router = _make_router(default="anthropic")
    provider = router.get_provider("llama-3-70b")
    assert provider is router.providers["anthropic"]


async def test_fallback_when_provider_raises() -> None:
    """If the primary provider fails, the router falls back to another."""
    failing = _FailingProvider()
    mock = MockLLMProvider()
    router = _make_router(openai=failing, anthropic=mock)

    response = await router.route(prompt="test", model="gpt-4o")
    assert isinstance(response, LLMResponse)
    assert response.content.startswith("Mock response")
