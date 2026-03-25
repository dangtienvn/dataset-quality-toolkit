# ADR-003: Row-Level Multi-Tenancy

## Status
Accepted

## Context
The SaaS application must support multiple tenants (organizations/users) with data isolation. Each tenant's data must be completely separated from other tenants. We need to choose between schema-per-tenant (separate PostgreSQL schemas) and row-level isolation (shared tables with tenant_id foreign key).

## Decision
Use row-level isolation with a `tenant_id` column on all tenant-scoped tables. Every query that touches tenant-scoped data includes a `WHERE tenant_id = :id` filter. The authenticated user's `tenant_id` is resolved from the JWT token via the `get_current_user` dependency.

## Alternatives Considered
- **Schema-per-tenant** — stronger isolation, each tenant gets its own PostgreSQL schema. Rejected because it adds complexity to migrations (must run per schema), connection management, and doesn't scale well beyond ~100 tenants.
- **Database-per-tenant** — maximum isolation but extreme operational complexity. Rejected because it's overkill for a SaaS starter and makes shared queries (admin metrics) very difficult.

## Consequences
- Positive: simple migrations (single schema), scales to thousands of tenants, easy to implement shared admin queries, standard PostgreSQL without extensions
- Negative: must be disciplined about always filtering by tenant_id (risk of data leaks if forgotten), less physical isolation between tenants
