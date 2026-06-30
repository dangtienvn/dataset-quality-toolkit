from pydantic import BaseModel
from typing import List, Optional

class Dataset(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    document_count: int = 0
