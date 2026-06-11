from fastapi.testclient import TestClient
from saas_starter.main import app

client = TestClient(app)

def test_rag_search():
    res = client.post("/api/v1/rag/search?query=test")
    assert res.status_code == 200
