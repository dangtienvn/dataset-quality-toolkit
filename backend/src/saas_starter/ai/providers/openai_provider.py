"""OpenAI LLM provider via httpx async."""

from decimal import Decimal

import httpx

from backend.src.saas_starter.ai.base import BaseLLMProvider, LLMResponse
from backend.src.saas_starter.core.config import settings

# Approximate pricing per 1M tokens (input / output)
_PRICING: dict[str, tuple[Decimal, Decimal]] = {
    "gpt-4o-mini": (Decimal("0.15"), Decimal("0.60")),
    "gpt-4o": (Decimal("2.50"), Decimal("10.00")),
}
_DEFAULT_PRICING = (Decimal("1.00"), Decimal("3.00"))


class OpenAIProvider(BaseLLMProvider):
    """OpenAI chat completions via REST API."""

    @property
    def provider_name(self) -> str:
        return "openai"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key or settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"

    def get_cost(self, model: str, input_tokens: int, output_tokens: int) -> Decimal:
        inp_price, out_price = _PRICING.get(model, _DEFAULT_PRICING)
        return (inp_price * input_tokens + out_price * output_tokens) / Decimal("1000000")

    async def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Call OpenAI chat completions endpoint."""
        model = model or settings.default_model
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": model, "messages": messages, "max_tokens": max_tokens},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()

        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        content = data["choices"][0]["message"]["content"]

        inp_price, out_price = _PRICING.get(model, _DEFAULT_PRICING)
        cost = (inp_price * input_tokens + out_price * output_tokens) / Decimal("1000000")

        return LLMResponse(
            content=content,
            model=model,
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
