# API Endpoints

Base URL: `http://localhost:8003/api/v1`

## Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration (creates tenant + owner) |
| POST | `/auth/login` | Login (returns JWT access + refresh tokens) |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Invalidate refresh token |
| GET | `/auth/me` | Get current user info |

## Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | List users in tenant (admin/owner only) |
| POST | `/users/invite` | Invite user to tenant (owner only) |
| PUT | `/users/{user_id}` | Update user |
| DELETE | `/users/{user_id}` | Deactivate user (soft-delete) |

## AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/chat` | Chat with AI model |
| POST | `/ai/summarize` | Summarize text |
| POST | `/ai/analyze` | Analyze document |
| GET | `/ai/usage` | AI usage statistics for tenant |

## Billing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/billing/plans` | List available plans |
| POST | `/billing/subscribe` | Create subscription (persists to DB) |
| POST | `/billing/cancel` | Cancel active subscription |
| GET | `/billing/portal` | Get Stripe billing portal URL |
| GET | `/billing/current` | Current subscription plan status |

## Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/stripe` | Stripe webhook handler (signature-verified) |

## GDPR

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gdpr/export` | Export tenant data (GDPR Art. 20) |
| DELETE | `/gdpr/tenant` | Delete all tenant data (GDPR Art. 17) |
| GET | `/gdpr/user/export` | Export user data (GDPR Art. 20) |
| DELETE | `/gdpr/user` | Delete user data (GDPR Art. 17) |
| POST | `/gdpr/anonymize-logs` | Anonymize audit logs |

## Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard` | Tenant dashboard (users, AI usage, subscription) |

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
