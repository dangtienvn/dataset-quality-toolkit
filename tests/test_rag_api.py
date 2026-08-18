from fastapi.testclient import TestClient
from saas_starter.main import app

client = TestClient(app)

def test_rag_search():
    res = client.post("/api/v1/rag/search?query=test")
    assert res.status_code == 200

# Updated audit checkpoint 2026-08-18 14:15
