import hashlib

class RedisSemanticCache:
    def __init__(self):
        self.cache = {}

    def _get_key(self, query: str) -> str:
        return hashlib.md5(query.encode("utf-8")).hexdigest()

    def get(self, query: str):
        return self.cache.get(self._get_key(query))

    def set(self, query: str, response: str):
        self.cache[self._get_key(query)] = response
