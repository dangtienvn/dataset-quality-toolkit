from saas_starter.knowledge.citations import CitationExtractor, FootnoteFormatter

def test_citations():
    e = CitationExtractor()
    c = e.extract_citations("According to specs [Source: doc1.pdf]")
    assert c == ["doc1.pdf"]
