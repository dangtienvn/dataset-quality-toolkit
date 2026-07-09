from saas_starter.knowledge.versioning import DatasetVersionControl

def test_versioning():
    vc = DatasetVersionControl()
    v = vc.create_version("ds-1", "v1.0.0")
    assert v["version"] == "v1.0.0"
