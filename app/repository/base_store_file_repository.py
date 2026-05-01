# -*- coding: utf-8 -*-
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.base_store_file import BaseStoreFile
from app.schemas.base_store_file import BaseStoreFileCreate


class BaseStoreFileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: BaseStoreFileCreate) -> BaseStoreFile:
        record = BaseStoreFile(
            id=uuid.uuid4(),
            filename=data.filename,
            description=data.description,
            store_name=data.store_name,
            status="processing",
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_after_upload(
        self,
        record_id: uuid.UUID,
        gemini_resource_name: str,
        store_name: Optional[str] = None,
    ) -> Optional[BaseStoreFile]:
        record = self.db.query(BaseStoreFile).filter(
            BaseStoreFile.id == record_id
        ).first()
        if not record:
            return None
        record.gemini_resource_name = gemini_resource_name
        record.status = "indexed"
        if store_name:
            record.store_name = store_name
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_by_store(self, store_name: str) -> list[BaseStoreFile]:
        return (
            self.db.query(BaseStoreFile)
            .filter(BaseStoreFile.store_name == store_name)
            .order_by(BaseStoreFile.created_at.desc())
            .all()
        )

    def list_all(self) -> list[BaseStoreFile]:
        return (
            self.db.query(BaseStoreFile)
            .order_by(BaseStoreFile.created_at.desc())
            .all()
        )

    def get_by_id(self, record_id: uuid.UUID) -> Optional[BaseStoreFile]:
        return (
            self.db.query(BaseStoreFile)
            .filter(BaseStoreFile.id == record_id)
            .first()
        )
