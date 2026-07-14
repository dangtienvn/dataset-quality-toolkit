from saas_starter.knowledge.synonyms import SynonymExpander

def test_synonyms():
    s = SynonymExpander()
    exp = s.expand("AI")
    assert "Artificial Intelligence" in exp
