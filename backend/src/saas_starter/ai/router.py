"""LLM router: routes requests to the appropriate provider (ADR-002)."""

import time

import structlog

from backend.src.saas_starter.ai.base import BaseLLMProvider, LLMResponse

logger = structlog.get_logger()


class LLMProviderError(Exception):
    """Raised when an LLM provider call fails."""

    def __init__(self, provider: str, message: str, cause: Exception | None = None) -> None:
        self.provider = provider
        super().__init__(f"[{provider}] {message}")
        self.__cause__ = cause


class AllProvidersFailedError(Exception):
    """Raised when all configured LLM providers have failed."""


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
        errors: list[LLMProviderError] = []

        start = time.monotonic()
        try:
            response = await primary.complete(prompt, system_prompt, model, max_tokens)
            response.latency_ms = int((time.monotonic() - start) * 1000)
            return response
        except (ConnectionError, TimeoutError, OSError, RuntimeError, ValueError) as exc:
            err = LLMProviderError(primary.provider_name, str(exc), cause=exc)
            errors.append(err)
            logger.warning("primary_provider_failed", model=model, error=str(exc))

        for name in fallback_names:
            start = time.monotonic()
            try:
                response = await self.providers[name].complete(
                    prompt, system_prompt, model, max_tokens
                )
                response.latency_ms = int((time.monotonic() - start) * 1000)
                return response
            except (ConnectionError, TimeoutError, OSError, RuntimeError, ValueError) as exc:
                err = LLMProviderError(name, str(exc), cause=exc)
                errors.append(err)
                logger.warning("fallback_provider_failed", provider=name, error=str(exc))

        raise AllProvidersFailedError(f"All LLM providers failed: {[str(e) for e in errors]}")
