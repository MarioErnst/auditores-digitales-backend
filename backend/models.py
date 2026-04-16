import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    audit_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default="active")

    chat_history = relationship("ChatHistory", back_populates="session")
    evidence = relationship("EvidenceMetadata", back_populates="session")

    def __repr__(self) -> str:
        return f"<Session id={self.id} audit_id={self.audit_id} status={self.status}>"


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="chat_history")

    def __repr__(self) -> str:
        return f"<ChatHistory id={self.id} session_id={self.session_id}>"


class EvidenceMetadata(Base):
    __tablename__ = "evidence_metadata"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    gcs_path = Column(String(500))
    file_ref = Column(String(255))
    status = Column(String(20), default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="evidence")

    def __repr__(self) -> str:
        return f"<EvidenceMetadata id={self.id} filename={self.filename} status={self.status}>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} event_type={self.event_type} status={self.status}>"
