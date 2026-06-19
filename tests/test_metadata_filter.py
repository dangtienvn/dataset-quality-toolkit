from saas_starter.rag.metadata_filter import MetadataFilter

def test_metadata_filter():
    f = MetadataFilter()
    docs = [{"metadata": {"tenant_id": "t1"}}, {"metadata": {"tenant_id": "t2"}}]
    res = f.filter(docs, {"tenant_id": "t1"})
    assert len(res) == 1
