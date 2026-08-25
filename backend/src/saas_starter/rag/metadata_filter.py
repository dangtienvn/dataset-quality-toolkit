class MetadataFilter:
    def filter(self, docs: list, criteria: dict):
        return [d for d in docs if all(d.get("metadata", {}).get(k) == v for k, v in criteria.items())]

# Updated audit checkpoint 2026-08-25 14:15
