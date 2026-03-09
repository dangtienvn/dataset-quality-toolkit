# ADR-004: AI Usage Tracking

## Status
Accepted

## Context
AI API calls cost money (tokens consumed). For usage-based billing, cost transparency, and abuse prevention, we need to track every LLM call with its metadata: tokens used, cost, latency, model, and user. This data feeds the AI usage dashboard and Stripe usage-based billing.

## Decision
Log every LLM call to a dedicated `ai_usage_log` database table with fields: user_id, tenant_id, model, provider, input_tokens, output_tokens, cost_usd, latency_ms, endpoint, timestamp. Aggregate data for dashboard views (daily/weekly/monthly). Trigger alerts when a tenant exceeds budget thresholds.

## Alternatives Considered
- **External analytics (Segment, Mixpanel)** — adds third-party dependency and latency. Rejected because we need real-time data for billing and budget alerts.
- **Log files only** — simpler but hard to query and aggregate. Rejected because dashboard and billing require structured, queryable data.

## Consequences
- Positive: real-time usage visibility, enables accurate usage-based billing, budget alerts prevent surprise costs, data for optimizing model selection
- Negative: additional database writes per LLM call (mitigated by async inserts), storage grows with usage (mitigated by periodic archival)
