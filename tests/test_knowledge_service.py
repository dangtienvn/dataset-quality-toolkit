from saas_starter.knowledge.service import KnowledgeBaseService

def test_create_dataset():
    srv = KnowledgeBaseService()
    ds = srv.create_dataset("Engineering Wiki")
    assert ds["name"] == "Engineering Wiki"
