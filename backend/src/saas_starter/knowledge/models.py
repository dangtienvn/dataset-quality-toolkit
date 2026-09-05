from pydantic import BaseModel
from typing import List, Optional

class Dataset(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    document_count: int = 0

# Updated audit checkpoint 2026-09-05 14:15
