"""Integration tests for AI API endpoints using MockLLMProvider."""

from httpx import AsyncClient

from tests.conftest import seed_tenant_and_user


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_chat_endpoint_returns_content(client: AsyncClient) -> None:
    """POST /ai/chat returns mock content."""
    _tenant, _user, token = await seed_tenant_and_user(
        email="ai-chat@test.com", tenant_slug="ai-chat"
    )
    resp = await client.post(
        "/api/v1/ai/chat",
        headers=_auth(token),
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "Mock response" in body["content"]
    assert body["usage"]["input_tokens"] == 10
    assert body["usage"]["output_tokens"] == 20


async def test_summarize_endpoint_works(client: AsyncClient) -> None:
    """POST /ai/summarize returns a summary."""
    _tenant, _user, token = await seed_tenant_and_user(
        email="ai-sum@test.com", tenant_slug="ai-sum"
    )
    resp = await client.post(
        "/api/v1/ai/summarize",
        headers=_auth(token),
        json={"text": "Long text to summarize.", "style": "concise"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "Mock response" in body["summary"]


async def test_analyze_endpoint_works(client: AsyncClient) -> None:
    """POST /ai/analyze returns analysis."""
    _tenant, _user, token = await seed_tenant_and_user(
        email="ai-analyze@test.com", tenant_slug="ai-analyze"
    )
    resp = await client.post(
        "/api/v1/ai/analyze",
        headers=_auth(token),
        json={"text": "Analyze this text.", "analysis_type": "sentiment"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "Mock response" in body["result"]


async def test_usage_tracked_after_ai_call(client: AsyncClient) -> None:
    """AI call creates a usage record visible via GET /ai/usage."""
    _tenant, _user, token = await seed_tenant_and_user(
        email="ai-usage@test.com", tenant_slug="ai-usage"
    )

    # Make an AI call
    await client.post(
        "/api/v1/ai/chat",
        headers=_auth(token),
        json={"messages": [{"role": "user", "content": "Track me"}]},
    )

    # Check usage
    resp = await client.get("/api/v1/ai/usage", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["calls_count"] >= 1
    assert body["total_tokens"] >= 30  # 10 input + 20 output


async def test_ai_requires_auth(client: AsyncClient) -> None:
    """AI endpoints return 401/422 without a token."""
    resp = await client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
    )
    assert resp.status_code in (401, 422)
