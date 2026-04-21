# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.rag_store import RagStore
from app.utils.logger import log_warning
from app.utils.uuid_helper import generate_uuid


class RagStoreRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def get_base_store(self) -> Optional[RagStore]:
        return (
            self.db.query(RagStore)
            .filter(RagStore.store_type == "base")
            .first()
        )

    def get_session_store(self, session_id: str) -> Optional[RagStore]:
        return (
            self.db.query(RagStore)
            .filter(
                RagStore.store_type == "session",
                RagStore.session_id == session_id,
            )
            .first()
        )

    def create_session_store(
        self,
        session_id: str,
        store_name: str,
        display_name: str,
    ) -> RagStore:
        store = RagStore(
            id=generate_uuid(),
            store_name=store_name,
            store_type="session",
            descripcion=display_name,
            archivos_count=0,
            session_id=session_id,
        )
        try:
            self.db.add(store)
            self.db.commit()
            self.db.refresh(store)
        except Exception as e:
            self.db.rollback()
            log_warning(f"Error creando session store para session_id={session_id}: {e}")
            raise
        return store
