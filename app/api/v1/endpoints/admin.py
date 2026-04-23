# -*- coding: utf-8 -*-
from datetime import datetime

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.core.exceptions import N8NUnavailableError
from app.schemas.documento import DocumentoUploadResponse
from app.services.n8n_service import n8n_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/documentos/", response_model=DocumentoUploadResponse, status_code=202)
async def upload_documento_base(
    file: UploadFile,
    descripcion: str = Form(default=""),
) -> DocumentoUploadResponse:
    filename = file.filename or ""
    contents = await file.read()
    try:
        result = await n8n_service.dispatch_upload_base(contents, filename, descripcion)
    except N8NUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return DocumentoUploadResponse(
        status=result.get("status", "processing"),
        filename=filename,
        descripcion=descripcion or None,
        store=result.get("store"),
        timestamp=datetime.utcnow(),
    )
