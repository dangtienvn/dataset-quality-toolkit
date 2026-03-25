# AI SaaS Starter

Production-ready full-stack AI SaaS boilerplate with multi-tenancy, subscription billing, and GDPR compliance.

![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![Next.js 14](https://img.shields.io/badge/Next.js_14-000?logo=nextdotjs&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169e1?logo=postgresql&logoColor=white) ![Stripe](https://img.shields.io/badge/Stripe-635bff?logo=stripe&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ed?logo=docker&logoColor=white) ![License MIT](https://img.shields.io/badge/License-MIT-green)

---

## Overview

A complete starter template for building AI-powered SaaS applications. Covers the full stack from authentication and billing to LLM integration and compliance — the kind of plumbing every SaaS needs but nobody wants to build twice.

**What makes this interesting:**
- Custom LLM abstraction layer that routes between OpenAI and Anthropic with automatic fallback
- Row-level multi-tenancy with tenant isolation enforced at every data access point
- Every AI call is metered (tokens, cost, latency, provider) for usage-based billing
- Stripe subscription lifecycle fully managed via webhooks
- GDPR export, deletion, and audit log anonymization built in from day one

## Architecture

```mermaid
graph LR
    Browser --> NextJS["Next.js 14"]
    NextJS -->|"/api/* proxy"| FastAPI["FastAPI"]
    FastAPI --> PostgreSQL["PostgreSQL"]
    FastAPI --> AI["AI Module"]
    FastAPI --> Stripe["Stripe"]
    FastAPI --> GDPR["GDPR Service"]
    AI --> OpenAI["OpenAI"]
    AI --> Anthropic["Anthropic"]
    Stripe -->|Webhooks| FastAPI
```

## Key Features

**AI Module** — Chat, summarize, analyze with pluggable LLM abstraction (OpenAI, Anthropic, custom providers)

**Multi-tenancy** — Row-level data isolation between tenants with `tenant_id` on every scoped table

**Auth & RBAC** — JWT access + refresh tokens, bcrypt hashing, roles: owner / admin / member

**Stripe Billing** — Three-tier subscriptions (free / starter / pro), webhook handlers, billing portal

**GDPR Compliance** — Tenant & user data export, deletion (Art. 17), audit log anonymization (Art. 20)

**Production Ready** — Docker Compose, GitHub Actions CI, 93% test coverage, structured logging

## Tech Stack

| Backend | Frontend |
|---|---|
| FastAPI 0.115+ | Next.js 14 |
| SQLAlchemy 2.0 (async) | TypeScript |
| PostgreSQL + asyncpg | Tailwind CSS |
| Alembic migrations | Axios |
| python-jose (JWT) | |
| Stripe API (httpx) | |
| structlog | |
| pydantic-settings v2 | |

## Getting Started

### With Docker (recommended)

```bash
git clone https://github.com/ForwardCodeSolutions/ai-saas-starter.git
cd ai-saas-starter
cp .env.example .env    # edit with your API keys
docker compose up -d
```

| Service | URL |
|---|---|
| API docs (Swagger) | http://localhost:8003/docs |
| Frontend | http://localhost:3000 |
| PostgreSQL | localhost:5433 |

### Local Development (without Docker)

**Prerequisites:** Python 3.11+, Node.js 20+, PostgreSQL, [uv](https://docs.astral.sh/uv/)

```bash
# Backend
cp .env.example .env          # configure DATABASE_URL and API keys
uv sync                       # install Python dependencies
cd backend && uv run alembic upgrade head && cd ..   # run migrations
make dev                      # or: uv run uvicorn backend.src.saas_starter.main:app --port 8003

# Frontend
cd frontend
npm install
npm run dev                   # http://localhost:3000
```

### Environment Variables

| Variable | Description | Required |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) | Yes |
| `OPENAI_API_KEY` | OpenAI API key | For AI features |
| `ANTHROPIC_API_KEY` | Anthropic API key | For AI features |
| `DEFAULT_LLM_PROVIDER` | `openai` or `anthropic` | No (default: openai) |
| `DEFAULT_MODEL` | Default model name | No (default: gpt-4o-mini) |
| `JWT_SECRET` | Secret for signing tokens — **change in production** | Yes |
| `STRIPE_SECRET_KEY` | Stripe secret key (test or live) | For billing |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | For billing |
| `STRIPE_PRICE_ID_STARTER` | Stripe Price ID for Starter plan | For billing |
| `STRIPE_PRICE_ID_PRO` | Stripe Price ID for Pro plan | For billing |
| `CORS_ORIGINS` | Comma-separated allowed origins | No (default: localhost:3000) |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | No (default: INFO) |

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register tenant + owner | — |
| POST | `/api/v1/auth/login` | Authenticate, get tokens | — |
| POST | `/api/v1/auth/refresh` | Refresh access token | — |
| POST | `/api/v1/auth/logout` | Revoke refresh token | — |
| GET | `/api/v1/auth/me` | Current user info | Yes |

### Users

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/users` | List tenant users | Admin+ |
| POST | `/api/v1/users/invite` | Invite user to tenant | Owner |
| PUT | `/api/v1/users/{id}` | Update role / status | Admin+ |
| DELETE | `/api/v1/users/{id}` | Deactivate user | Owner |

### AI

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/ai/chat` | Chat completion | Yes |
| POST | `/api/v1/ai/summarize` | Text summarization | Yes |
| POST | `/api/v1/ai/analyze` | Text analysis | Yes |
| GET | `/api/v1/ai/usage` | Usage stats (30 days) | Yes |

### Billing

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/billing/plans` | List available plans | — |
| POST | `/api/v1/billing/subscribe` | Create subscription | Yes |
| POST | `/api/v1/billing/cancel` | Cancel subscription | Yes |
| GET | `/api/v1/billing/portal` | Stripe billing portal | Yes |
| GET | `/api/v1/billing/current` | Current plan & status | Yes |

### GDPR

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/gdpr/export` | Export tenant data | Yes |
| DELETE | `/api/v1/gdpr/tenant` | Delete all tenant data | Yes |
| GET | `/api/v1/gdpr/user/export` | Export user data | Yes |
| DELETE | `/api/v1/gdpr/user` | Delete user data | Yes |
| POST | `/api/v1/gdpr/anonymize-logs` | Anonymize audit logs | Yes |

### Admin & System

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/api/v1/admin/dashboard` | Tenant stats dashboard | Yes |
| POST | `/api/v1/webhooks/stripe` | Stripe webhook handler | Signature |
| GET | `/api/v1/health` | Health check | — |

## Subscription Plans

| Plan | Price | AI Calls | Users | Support |
|---|---|---|---|---|
| **Free** | $0 | 100/month | 1 | Community |
| **Starter** | $29/mo | 5,000/month | 5 | Email + priority models |
| **Pro** | $99/mo | Unlimited | Unlimited | Priority + all models + custom integrations |

## Design Decisions

| ADR | Title | Summary |
|---|---|---|
| [ADR-001](docs/decisions/ADR-001-fastapi-react.md) | FastAPI + React | Async Python + Next.js over Django/Node alternatives |
| [ADR-002](docs/decisions/ADR-002-llm-abstraction.md) | LLM Abstraction Layer | Custom provider interface over LangChain for control and simplicity |
| [ADR-003](docs/decisions/ADR-003-multi-tenancy.md) | Row-Level Multi-tenancy | `tenant_id` FK on all scoped tables, not schema-per-tenant |
| [ADR-004](docs/decisions/ADR-004-ai-usage-tracking.md) | AI Usage Tracking | Dedicated table tracking tokens, cost, model per call |
| [ADR-005](docs/decisions/ADR-005-stripe-billing.md) | Stripe Billing | Subscription tiers with webhook lifecycle management |

## Testing

69 tests across unit and integration suites with 93% code coverage.

```
Unit tests:     31 tests (models, security, auth, LLM router, Stripe, GDPR service)
Integration:    38 tests (auth API, AI API, billing API, GDPR API, full SaaS flow)
```

```bash
make test          # run all tests with coverage
make lint          # ruff check + format
make check         # lint + test (run before every commit)
```

## Project Structure

```
├── backend/src/saas_starter/
│   ├── ai/                    # LLM abstraction layer
│   │   ├── providers/         # OpenAI, Anthropic, Mock
│   │   ├── features/          # chat, summarize, analyze
│   │   └── router.py          # model-prefix routing + fallback
│   ├── api/v1/                # FastAPI routers
│   ├── core/                  # config, database, security, exceptions
│   ├── models/                # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response
│   └── services/              # auth, stripe, gdpr, usage
├── frontend/
│   ├── app/                   # Next.js 14 app router pages
│   ├── components/            # Navbar, AuthGuard
│   └── lib/                   # API client (axios)
├── tests/
│   ├── unit/                  # 6 unit test modules
│   └── integration/           # 5 integration test modules
├── docs/
│   ├── decisions/             # 5 Architecture Decision Records
│   ├── api.md                 # API endpoint reference
│   ├── architecture.md        # System design overview
│   ├── code-conventions.md    # Code style guide
│   └── testing-strategy.md    # Testing approach
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

## Disclaimer

> This is a starter template. Review and update security settings,
> secret keys, and CORS configuration before production use.

## License

MIT © 2026 ForwardCodeSolutions
