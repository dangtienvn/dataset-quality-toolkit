import hashlib

def compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Deduplicator:
    def is_duplicate(self, existing_hashes: set, text: str) -> bool:
        return compute_content_hash(text) in existing_hashes
