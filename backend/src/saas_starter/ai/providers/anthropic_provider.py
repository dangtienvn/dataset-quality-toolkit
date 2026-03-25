"""Anthropic LLM provider via httpx async."""

from decimal import Decimal

import httpx

from backend.src.saas_starter.ai.base import BaseLLMProvider, LLMResponse
from backend.src.saas_starter.core.config import settings

# Approximate pricing per 1M tokens (input / output)
_PRICING: dict[str, tuple[Decimal, Decimal]] = {
    "claude-sonnet-4-20250514": (Decimal("3.00"), Decimal("15.00")),
    "claude-haiku-4-20250414": (Decimal("0.80"), Decimal("4.00")),
}
_DEFAULT_PRICING = (Decimal("3.00"), Decimal("15.00"))


class AnthropicProvider(BaseLLMProvider):
    """Anthropic messages API via REST."""

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key or settings.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"

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
        """Call Anthropic messages endpoint."""
        model = model or "claude-sonnet-4-20250514"
        body: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            body["system"] = system_prompt

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=body,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()

        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        content = data["content"][0]["text"]

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
