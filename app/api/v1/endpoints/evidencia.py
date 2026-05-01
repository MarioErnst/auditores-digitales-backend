# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import (
    EvidenceNotFoundError,
    FileTooLargeError,
    InvalidFileExtensionError,
    SessionNotFoundError,
)
from app.core.security import verify_api_key
from app.schemas.evidence import EvidenceListItem, EvidenceUploadResponse
from app.services.evidence_service import EvidenceService

router = APIRouter(
    prefix="/evidencia",
    tags=["evidencia"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/", response_model=list[EvidenceListItem])
def list_evidence(
    session_id: str = Query(...),
    db: DBSession = Depends(get_db),
) -> list[EvidenceListItem]:
    service = EvidenceService(db)
    try:
        return service.list_evidence(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=EvidenceUploadResponse, status_code=202)
async def upload_evidence(
    file: UploadFile,
    session_id: str = Query(...),
    db: DBSession = Depends(get_db),
) -> EvidenceUploadResponse:
    filename = file.filename or ""
    contents = await file.read()
    service = EvidenceService(db)
    try:
        return await service.upload_evidence(filename, contents, session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidFileExtensionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))


@router.delete("/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
    session_id: str = Query(...),
    db: DBSession = Depends(get_db),
) -> dict:
    service = EvidenceService(db)
    try:
        filename = await service.delete_evidence(evidence_id, session_id)
    except EvidenceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"deleted": True, "filename": filename}
