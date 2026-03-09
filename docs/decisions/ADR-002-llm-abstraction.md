# ADR-002: Unified LLM Abstraction Layer

## Status
Accepted

## Context
The application needs to support multiple LLM providers (OpenAI, Anthropic, potentially local models). Hardcoding a single provider would create vendor lock-in and make it difficult to switch or compare models. Users should be able to change providers via configuration without code changes.

## Decision
Create an abstract base class `LLMProvider` with methods: `generate()`, `stream()`, `get_cost()`. Concrete implementations for each provider (OpenAI, Anthropic). Provider selection via `DEFAULT_LLM_PROVIDER` environment variable. A factory function instantiates the correct provider at runtime.

## Alternatives Considered
- **LangChain** — provides similar abstraction but adds a heavy dependency with its own opinions and complexity. Rejected because we want a minimal, transparent layer we fully control.
- **Direct SDK calls everywhere** — simplest approach but creates tight coupling to one provider. Rejected because switching providers would require touching every call site.
- **LiteLLM** — lightweight proxy but adds another service to manage. Rejected because an in-process abstraction is simpler for our use case.

## Consequences
- Positive: swap providers with a single env var change, easy to add new providers, cost tracking per provider, transparent and debuggable
- Negative: must maintain provider implementations ourselves, new provider features may lag behind native SDKs
