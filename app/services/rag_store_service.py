# -*- coding: utf-8 -*-
from typing import List

from sqlalchemy.orm import Session as DBSession

from app.repository.rag_store_repository import RagStoreRepository
from app.schemas.rag_store import RagStoreResponse


class RagStoreService:
    def __init__(self, db: DBSession) -> None:
        self.repo = RagStoreRepository(db)

    def list_all(self) -> List[RagStoreResponse]:
        stores = self.repo.list_all()
        return [RagStoreResponse.model_validate(s) for s in stores]
