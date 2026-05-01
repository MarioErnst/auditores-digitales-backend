# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String

from app.database import Base
from app.utils.uuid_helper import generate_uuid


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} event_type={self.event_type} "
            f"status={self.status}>"
        )
