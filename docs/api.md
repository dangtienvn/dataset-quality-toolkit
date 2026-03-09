# API Endpoints

Base URL: `http://localhost:8003/api/v1`

## Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | User registration |
| POST | `/auth/login` | Login (returns JWT) |
| POST | `/auth/refresh` | Refresh access token |

## AI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/chat` | Chat with AI |
| POST | `/ai/summarize` | Summarize text |
| POST | `/ai/analyze` | Analyze document |

## AI Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ai/usage` | AI usage statistics |
| GET | `/ai/costs` | AI costs by period |

## Billing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/billing/subscribe` | Create subscription |
| GET | `/billing/status` | Subscription status |
| POST | `/billing/webhook` | Stripe webhook handler |

## GDPR

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/gdpr/export` | Export user data (JSON) |
| DELETE | `/gdpr/delete` | Delete all user data |

## Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List users (admin only) |
| GET | `/admin/metrics` | System metrics (admin only) |

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
