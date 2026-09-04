from saas_starter.rag.summary import DocumentSummarizer

def test_summary():
    s = DocumentSummarizer()
    res = s.summarize("A long text content for testing summary", 10)
    assert len(res) <= 15

# Updated audit checkpoint 2026-09-04 09:30
