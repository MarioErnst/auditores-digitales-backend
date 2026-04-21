# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import (
    FileTooLargeError,
    InvalidFileExtensionError,
    SessionNotFoundError,
)
from app.schemas.evidence import EvidenceUploadResponse
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidencia", tags=["evidencia"])


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
