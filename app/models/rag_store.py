# -*- coding: utf-8 -*-
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RagStore(Base):
    __tablename__ = "rag_stores"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_name = Column(String(255), nullable=False)
    store_type = Column(String(20), nullable=False)  # 'base' | 'session'
    description = Column(Text, nullable=True)
    file_count = Column(Integer, default=0, nullable=True)
    session_id = Column(
        String(36),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("Session", back_populates="rag_stores")

    def __repr__(self) -> str:
        return (
            f"<RagStore id={self.id} store_name={self.store_name} "
            f"store_type={self.store_type}>"
        )
