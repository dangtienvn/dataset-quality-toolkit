from saas_starter.core.audit import AuditLogger

def test_audit():
    al = AuditLogger()
    al.log_event("usr-1", "query_rag", "ds-1")
    assert len(al.logs) == 1
