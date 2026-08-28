import hashlib

def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Deduplicator:
    def is_duplicate(self, existing_hashes: set, text: str) -> bool:
        return compute_content_hash(text) in existing_hashes

# Updated audit checkpoint 2026-08-28 09:30

# Updated audit checkpoint 2026-08-28 14:15
