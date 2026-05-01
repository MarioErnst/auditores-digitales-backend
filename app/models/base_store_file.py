# -*- coding: utf-8 -*-
import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class BaseStoreFile(Base):
    __tablename__ = "base_store_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    gemini_resource_name = Column(String, nullable=True)
    store_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="processing")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<BaseStoreFile id={self.id} filename={self.filename} status={self.status}>"
