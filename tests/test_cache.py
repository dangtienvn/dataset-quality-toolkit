from saas_starter.copilot.cache import RedisSemanticCache

def test_cache():
    c = RedisSemanticCache()
    c.set("what is python?", "Python is a language")
    assert c.get("what is python?") == "Python is a language"
