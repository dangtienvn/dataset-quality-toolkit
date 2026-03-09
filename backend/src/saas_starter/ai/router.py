"""LLM router: routes requests to the appropriate provider (ADR-002)."""

import structlog

from backend.src.saas_starter.ai.base import BaseLLMProvider, LLMResponse

logger = structlog.get_logger()


class LLMRouter:
    """Routes LLM requests to providers based on model name."""

    def __init__(
        self,
        providers: dict[str, BaseLLMProvider],
        default_provider: str,
    ) -> None:
        self.providers = providers
        self.default_provider = default_provider

    def get_provider(self, model: str) -> BaseLLMProvider:
        """Select a provider based on model name prefix."""
        if model.startswith("gpt-") and "openai" in self.providers:
            return self.providers["openai"]
        if model.startswith("claude-") and "anthropic" in self.providers:
            return self.providers["anthropic"]
        return self.providers[self.default_provider]

    async def route(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Route a request with fallback on provider failure."""
        primary = self.get_provider(model)
        fallback_names = [name for name, p in self.providers.items() if p is not primary]

        try:
            return await primary.complete(prompt, system_prompt, model, max_tokens)
        except Exception:
            logger.warning("primary_provider_failed", model=model)

        for name in fallback_names:
            try:
                return await self.providers[name].complete(prompt, system_prompt, model, max_tokens)
            except Exception:
                logger.warning("fallback_provider_failed", provider=name)

        raise RuntimeError("All LLM providers failed")
