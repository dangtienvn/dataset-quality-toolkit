# Testing Strategy

## Overview

The project maintains **93% code coverage** across 69 tests. External services (OpenAI, Anthropic, Stripe) are mocked in all tests to ensure fast, deterministic, and offline-capable test runs.

## Structure

```
tests/
├── conftest.py              # Shared fixtures: async SQLite engine, test client, seed helpers
├── unit/                    # Isolated logic with mocked dependencies
│   ├── test_auth.py         # Auth service (register, login, refresh, logout)
│   ├── test_security.py     # JWT creation, decoding, expiry
│   ├── test_models.py       # ORM model constraints and relationships
│   ├── test_llm_router.py   # LLM routing, fallback, provider selection
│   ├── test_stripe_service.py  # Webhook signature verification, event handling
│   └── test_gdpr_service.py # Data export, deletion, anonymization
└── integration/             # Full HTTP request/response through FastAPI
    ├── test_auth_api.py     # Registration, login, token refresh, RBAC
    ├── test_ai_api.py       # Chat, summarize, analyze, usage tracking
    ├── test_billing_api.py  # Plans, subscribe, cancel, portal
    ├── test_gdpr_api.py     # Export, delete, anonymize + admin dashboard
    └── test_full_saas_flow.py  # End-to-end SaaS journey, multi-tenant isolation
```

## Testing Principles

- **Every new feature needs tests** — unit tests for business logic, integration tests for API endpoints
- **Mock external services** — LLM providers use `MockLLMProvider`, Stripe uses in-process mock classes
- **Async-first** — all tests use `pytest-asyncio` with async fixtures and `httpx.AsyncClient`
- **In-memory SQLite** — integration tests use an async SQLite engine (via `aiosqlite`) for speed
- **Tenant isolation** — tests verify that data from one tenant is never accessible to another

## Running Tests

```bash
make test          # All tests with coverage report
make check         # Lint + tests (recommended before commits)

# Selective runs
uv run pytest tests/unit/ -v              # Unit tests only
uv run pytest tests/integration/ -v       # Integration tests only
uv run pytest tests/ -k "test_auth" -v    # Filter by name
```

## Coverage

Coverage excludes real HTTP provider implementations (OpenAI, Anthropic, Stripe service) since those are integration points tested via mocks. See `pyproject.toml` `[tool.coverage.run]` for the full omit list.
