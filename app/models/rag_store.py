# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.uuid_helper import generate_uuid


class RagStore(Base):
    __tablename__ = "rag_stores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    store_name = Column(String(255), nullable=False)
    store_type = Column(String(20), nullable=False)  # 'base' | 'session'
    descripcion = Column(Text, nullable=True)
    archivos_count = Column(Integer, default=0, nullable=False)
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
