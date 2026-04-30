# -*- coding: utf-8 -*-
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.schemas.rag_store import RagStoreResponse
from app.services.rag_store_service import RagStoreService

router = APIRouter(prefix="/rag-stores", tags=["rag-stores"])


@router.get("/", response_model=List[RagStoreResponse])
def list_rag_stores(db: DBSession = Depends(get_db)) -> List[RagStoreResponse]:
    service = RagStoreService(db)
    return service.list_all()
