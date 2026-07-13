class SynonymExpander:
    def __init__(self, synonym_map: dict = None):
        self.synonym_map = synonym_map or {"AI": ["Artificial Intelligence", "Machine Learning"]}

    def expand(self, keyword: str) -> list:
        return self.synonym_map.get(keyword, [keyword])
