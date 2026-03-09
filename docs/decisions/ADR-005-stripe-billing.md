# ADR-005: Stripe Subscription + Usage-Based Billing

## Status
Accepted

## Context
The SaaS needs a billing model that covers infrastructure costs and scales with AI usage. Pure subscription leaves heavy users under-charged. Pure usage-based creates unpredictable revenue. We need a hybrid approach.

## Decision
Use Stripe for subscription tiers with usage-based overage:
- **Free tier**: limited AI calls per month (e.g., 100)
- **Starter tier**: higher limits, priority models
- **Pro tier**: highest limits, all models, priority support
- Usage beyond tier limits billed per token via Stripe usage records

Stripe webhooks handle subscription lifecycle (created, updated, cancelled, payment failed).

## Alternatives Considered
- **Paddle** — handles tax compliance better but smaller ecosystem and fewer integrations. Rejected because Stripe's developer experience and documentation are superior.
- **LemonSqueezy** — simpler setup but less control over usage-based billing. Rejected because we need granular usage metering.
- **Self-built billing** — maximum control but enormous implementation effort and regulatory risk. Rejected because Stripe handles PCI compliance, tax, and payment processing.

## Consequences
- Positive: predictable base revenue + usage scaling, Stripe handles payment complexity, webhooks enable real-time subscription status, well-documented API
- Negative: Stripe fees (~2.9% + 30c per transaction), vendor dependency on Stripe, webhook reliability must be handled (idempotency, retries)
