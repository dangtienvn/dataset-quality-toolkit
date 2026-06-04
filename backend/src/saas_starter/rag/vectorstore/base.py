from typing import List, Dict, Any

class BaseVectorStore:
    async def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        raise NotImplementedError

    async def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        raise NotImplementedError
