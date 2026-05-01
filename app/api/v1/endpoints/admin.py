# -*- coding: utf-8 -*-
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import N8NUnavailableError
from app.core.security import verify_api_key
from app.repository.base_store_file_repository import BaseStoreFileRepository
from app.schemas.base_store_file import BaseStoreFileCreate, BaseStoreFileResponse
from app.schemas.documento import DocumentoUploadResponse
from app.services.n8n_service import n8n_service
from app.utils.logger import log_warning

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/documentos/", response_model=list[BaseStoreFileResponse])
async def list_documentos_base(
    db: DBSession = Depends(get_db),
) -> list[BaseStoreFileResponse]:
    repo = BaseStoreFileRepository(db)
    return repo.list_all()


@router.post("/documentos/", response_model=DocumentoUploadResponse, status_code=202)
async def upload_documento_base(
    file: UploadFile,
    description: str = Form(default=""),
    db: DBSession = Depends(get_db),
) -> DocumentoUploadResponse:
    filename = file.filename or ""
    contents = await file.read()

    repo = BaseStoreFileRepository(db)
    file_record = repo.create(BaseStoreFileCreate(
        filename=filename,
        description=description or None,
        store_name="",
    ))

    try:
        result = await n8n_service.dispatch_upload_base(contents, filename, description)
    except N8NUnavailableError as e:
        log_warning(f"N8N no disponible para upload base (file_id={file_record.id}): {e}")
        raise HTTPException(status_code=503, detail=str(e))

    store_name = result.get("store") or ""
    gemini_resource_name = result.get("gemini_resource_name") or ""

    repo.update_after_upload(
        record_id=file_record.id,
        gemini_resource_name=gemini_resource_name,
        store_name=store_name,
    )

    return DocumentoUploadResponse(
        status=result.get("status", "processing"),
        filename=filename,
        description=description or None,
        store=store_name or None,
        gemini_resource_name=gemini_resource_name or None,
        file_id=file_record.id,
        timestamp=datetime.utcnow(),
    )
