# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.security import verify_api_key
from app.schemas.rag_store import RagStoreResponse
from app.services.rag_store_service import RagStoreService

router = APIRouter(
    prefix="/rag-stores",
    tags=["rag-stores"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/", response_model=list[RagStoreResponse])
async def list_rag_stores(db: DBSession = Depends(get_db)) -> list[RagStoreResponse]:
    service = RagStoreService(db)
    return service.list_all()
