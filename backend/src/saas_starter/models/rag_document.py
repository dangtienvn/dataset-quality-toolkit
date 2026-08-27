from sqlalchemy import Column, String, Integer, DateTime, Text
from saas_starter.core.database import Base
from datetime import datetime

class RAGDocument(Base):
    __tablename__ = "rag_documents"
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    content_hash = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Updated audit checkpoint 2026-08-27 14:15
