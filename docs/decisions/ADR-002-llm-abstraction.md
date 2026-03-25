# ADR-002: Unified LLM Abstraction Layer

## Status
Accepted

## Context
The application needs to support multiple LLM providers (OpenAI, Anthropic, potentially local models). Hardcoding a single provider would create vendor lock-in and make it difficult to switch or compare models. Users should be able to change providers via configuration without code changes.

## Decision
Create an abstract base class `BaseLLMProvider` with methods: `complete()`, `stream()`, `get_cost()`, and a `provider_name` property. Concrete implementations for each provider (OpenAI, Anthropic, Mock for testing). Provider selection via `DEFAULT_LLM_PROVIDER` environment variable. An `LLMRouter` class selects the correct provider at runtime based on model name prefix and provides fallback to alternative providers on failure.

### Interface
- `complete(prompt, system_prompt, model, max_tokens) -> LLMResponse` — synchronous completion
- `stream(prompt, system_prompt, model, max_tokens) -> AsyncIterator[str]` — streaming tokens (default: falls back to `complete()`)
- `get_cost(model, input_tokens, output_tokens) -> Decimal` — cost estimation per provider
- `provider_name: str` — identifier for usage tracking

### LLMResponse
Contains: `content`, `model`, `provider`, `input_tokens`, `output_tokens`, `cost_usd`, `latency_ms`.

## Alternatives Considered
- **LangChain** — provides similar abstraction but adds a heavy dependency with its own opinions and complexity. Rejected because we want a minimal, transparent layer we fully control.
- **Direct SDK calls everywhere** — simplest approach but creates tight coupling to one provider. Rejected because switching providers would require touching every call site.
- **LiteLLM** — lightweight proxy but adds another service to manage. Rejected because an in-process abstraction is simpler for our use case.

## Consequences
- Positive: swap providers with a single env var change, easy to add new providers, cost tracking per provider, transparent and debuggable
- Negative: must maintain provider implementations ourselves, new provider features may lag behind native SDKs
