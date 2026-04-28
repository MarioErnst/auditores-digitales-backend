# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import SessionNotFoundError
from app.repository.chat_repository import ChatRepository
from app.schemas.session import SessionCreate, SessionResponse
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=201)
def create_session(
    body: SessionCreate, db: DBSession = Depends(get_db)
) -> SessionResponse:
    service = SessionService(db)
    return service.create_session(audit_id=body.audit_id)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str, db: DBSession = Depends(get_db)
) -> SessionResponse:
    service = SessionService(db)
    try:
        return service.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def list_sessions(db: DBSession = Depends(get_db)):
    service = SessionService(db)
    return service.list_sessions()


@router.get("/{session_id}/messages")
def list_session_messages(session_id: str, db: DBSession = Depends(get_db)):
    service = SessionService(db)
    if not service.get_session_or_none(session_id):
        raise HTTPException(status_code=404, detail=f"Sesion {session_id} no existe")
    repo = ChatRepository(db)
    return [
        {
            "id": m.id,
            "question": m.question,
            "answer": m.answer,
            "created_at": m.created_at,
        }
        for m in repo.list_by_session(session_id)
    ]
