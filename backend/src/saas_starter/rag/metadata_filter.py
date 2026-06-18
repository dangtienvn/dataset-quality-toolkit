class MetadataFilter:
    def filter(self, docs: list, criteria: dict):
        return [d for d in docs if all(d.get("metadata", {}).get(k) == v for k, v in criteria.items())]
