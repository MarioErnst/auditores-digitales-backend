# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import SessionNotFoundError
from app.schemas.session import (
    SessionCreate,
    SessionListResponse,
    SessionResponse,
    SessionUpdateRequest,
)
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=SessionListResponse)
def list_sessions(db: DBSession = Depends(get_db)) -> SessionListResponse:
    service = SessionService(db)
    return service.list_sessions()


@router.post("/", response_model=SessionResponse, status_code=201)
def create_session(
    body: SessionCreate, db: DBSession = Depends(get_db)
) -> SessionResponse:
    service = SessionService(db)
    return service.create_session(audit_name=body.audit_name, audit_id=body.audit_id)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str, db: DBSession = Depends(get_db)
) -> SessionResponse:
    service = SessionService(db)
    try:
        return service.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: str,
    body: SessionUpdateRequest,
    db: DBSession = Depends(get_db),
) -> SessionResponse:
    service = SessionService(db)
    try:
        return service.update_audit_name(session_id, body.audit_name)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
