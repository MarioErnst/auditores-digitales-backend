# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from app.core.constants import DEFAULT_SESSION_STATUS
from app.database import Base
from app.utils.uuid_helper import generate_uuid


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    audit_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default=DEFAULT_SESSION_STATUS)

    chat_history = relationship("ChatHistory", back_populates="session")
    evidence = relationship("EvidenceMetadata", back_populates="session")
    rag_stores = relationship("RagStore", back_populates="session")

    def __repr__(self) -> str:
        return f"<Session id={self.id} audit_id={self.audit_id} status={self.status}>"
