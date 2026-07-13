from saas_starter.knowledge.export import KnowledgeExporter

def test_export():
    e = KnowledgeExporter()
    res = e.export_dataset({"id": "ds-1"})
    assert "ds-1" in res
