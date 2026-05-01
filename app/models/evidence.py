# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship

from app.core.constants import DEFAULT_EVIDENCE_STATUS
from app.database import Base
from app.utils.uuid_helper import generate_uuid


class EvidenceMetadata(Base):
    __tablename__ = "evidence_metadata"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    gemini_resource_name = Column(String(500), nullable=True)
    store_name = Column(String(255), nullable=True)
    # Deprecated: residuo de arquitectura anterior con GCS.
    # Siempre NULL. Candidata a eliminar en sprint futuro.
    gcs_path = Column(String(500))
    gemini_ref = Column(String(255))
    status = Column(String(20), default=DEFAULT_EVIDENCE_STATUS, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    session = relationship("Session", back_populates="evidence")

    def __repr__(self) -> str:
        return (
            f"<EvidenceMetadata id={self.id} filename={self.filename} "
            f"status={self.status}>"
        )
