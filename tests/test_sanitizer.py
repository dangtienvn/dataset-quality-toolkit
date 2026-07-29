from saas_starter.core.sanitizer import HTMLSanitizer

def test_sanitizer():
    s = HTMLSanitizer()
    res = s.sanitize("<script>alert(1)</script>")
    assert "<script>" not in res
