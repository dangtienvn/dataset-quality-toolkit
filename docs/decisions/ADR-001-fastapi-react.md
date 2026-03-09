# ADR-001: FastAPI + React over Django, Node.js, or Wasp

## Status
Accepted

## Context
We need to choose a backend framework and frontend stack for a full-stack AI SaaS boilerplate. The project must integrate heavily with Python AI libraries (OpenAI, Anthropic SDKs), provide auto-generated API documentation, and use a frontend stack that is widely demanded on the freelance market.

## Decision
**Backend: FastAPI.** Async-native, auto-generates OpenAPI docs, and stays within the Python ecosystem where all major AI/ML libraries live. No language switching between backend and AI code.

**Frontend: React/Next.js with Tailwind CSS and shadcn/ui.** The most in-demand frontend stack on Upwork and similar platforms. Server-side rendering, excellent developer experience, and a rich component ecosystem.

## Alternatives Considered
- **Django** — more opinionated and monolithic, Django REST Framework adds boilerplate, async support is still catching up. Rejected because FastAPI is leaner and better suited for API-first architecture.
- **Node.js (Express/Fastify)** — would require maintaining two languages (JS backend + Python AI). Rejected because it adds complexity and splits the codebase.
- **Wasp** — interesting full-stack framework but less flexible, smaller community, harder to customize. Rejected because it limits architectural control.

## Consequences
- Positive: single language (Python) for backend + AI, excellent async performance, auto OpenAPI docs, React skills are highly transferable
- Negative: two separate deployments (backend + frontend), need to manage CORS, slightly more complex project structure
