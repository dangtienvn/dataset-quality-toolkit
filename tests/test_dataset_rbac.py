from saas_starter.knowledge.rbac import DatasetRBAC

def test_rbac():
    rbac = DatasetRBAC()
    assert rbac.check_access("admin", "ds-1", "write") is True
    assert rbac.check_access("viewer", "ds-1", "write") is False
