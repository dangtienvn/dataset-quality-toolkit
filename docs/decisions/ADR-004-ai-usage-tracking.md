# ADR-004: AI Usage Tracking

## Status
Accepted

## Context
AI API calls cost money (tokens consumed). For usage-based billing, cost transparency, and abuse prevention, we need to track every LLM call with its metadata: tokens used, cost, latency, model, and user. This data feeds the AI usage dashboard and Stripe usage-based billing.

## Decision
Log every LLM call to a dedicated `ai_usages` database table with fields: `id`, `tenant_id`, `user_id`, `model`, `provider`, `input_tokens`, `output_tokens`, `cost_usd`, `latency_ms`, `feature`, `endpoint`, `created_at`, `updated_at`. Aggregate data for dashboard views (daily/weekly/monthly). Trigger alerts when a tenant exceeds budget thresholds.

### Model: `AIUsage`
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID FK | Multi-tenancy isolation |
| user_id | UUID FK | Which user made the call |
| model | String(100) | LLM model used (e.g. `gpt-4o-mini`) |
| provider | String(100) | Provider name (e.g. `openai`, `anthropic`) |
| input_tokens | Integer | Tokens sent to LLM |
| output_tokens | Integer | Tokens received from LLM |
| cost_usd | Numeric(10,6) | Estimated cost in USD |
| latency_ms | Integer | Response time in milliseconds |
| feature | String(100) | Feature used (e.g. `chat`, `summarize`, `analyze`) |
| endpoint | String(255) | API endpoint that triggered the call |
| created_at | DateTime | Timestamp |

## Alternatives Considered
- **External analytics (Segment, Mixpanel)** — adds third-party dependency and latency. Rejected because we need real-time data for billing and budget alerts.
- **Log files only** — simpler but hard to query and aggregate. Rejected because dashboard and billing require structured, queryable data.

## Consequences
- Positive: real-time usage visibility, enables accurate usage-based billing, budget alerts prevent surprise costs, data for optimizing model selection
- Negative: additional database writes per LLM call (mitigated by async inserts), storage grows with usage (mitigated by periodic archival)
