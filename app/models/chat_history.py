# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.constants import CHAT_STATUS_PROCESSING
from app.database import Base
from app.utils.uuid_helper import generate_uuid


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    request_id = Column(String(36), index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    sources = Column(JSON)
    status = Column(String(20), default=CHAT_STATUS_PROCESSING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="chat_history")

    def __repr__(self) -> str:
        return f"<ChatHistory id={self.id} session_id={self.session_id}>"
