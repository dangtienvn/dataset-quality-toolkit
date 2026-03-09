# ADR-003: Row-Level Multi-Tenancy

## Status
Accepted

## Context
The SaaS application must support multiple tenants (organizations/users) with data isolation. Each tenant's data must be completely separated from other tenants. We need to choose between schema-per-tenant (separate PostgreSQL schemas) and row-level isolation (shared tables with tenant_id foreign key).

## Decision
Use row-level isolation with a `tenant_id` column on all tenant-scoped tables. All queries are filtered by `tenant_id` automatically via SQLAlchemy query hooks or middleware.

## Alternatives Considered
- **Schema-per-tenant** — stronger isolation, each tenant gets its own PostgreSQL schema. Rejected because it adds complexity to migrations (must run per schema), connection management, and doesn't scale well beyond ~100 tenants.
- **Database-per-tenant** — maximum isolation but extreme operational complexity. Rejected because it's overkill for a SaaS starter and makes shared queries (admin metrics) very difficult.

## Consequences
- Positive: simple migrations (single schema), scales to thousands of tenants, easy to implement shared admin queries, standard PostgreSQL without extensions
- Negative: must be disciplined about always filtering by tenant_id (risk of data leaks if forgotten), less physical isolation between tenants
