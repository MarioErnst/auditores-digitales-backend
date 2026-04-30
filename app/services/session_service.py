# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.core.exceptions import SessionNotFoundError
from app.models.session import Session
from app.repository.session_repository import SessionRepository
from app.schemas.session import SessionListItem, SessionListResponse


class SessionService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.repo = SessionRepository(db)

    def create_session(self, audit_name: str, audit_id: Optional[str] = None) -> Session:
        return self.repo.create(audit_name=audit_name, audit_id=audit_id)

    def get_session(self, session_id: str) -> Session:
        session = self.repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        return session

    def get_session_or_none(self, session_id: str) -> Optional[Session]:
        return self.repo.get(session_id)

    def list_sessions(self) -> SessionListResponse:
        rows = self.repo.list_all()
        items = [
            SessionListItem(
                id=session.id,
                audit_name=session.audit_name,
                created_at=session.created_at,
                evidencias_count=count,
                status=session.status,
            )
            for session, count in rows
        ]
        return SessionListResponse(items=items, total=len(items))

    def update_audit_name(self, session_id: str, audit_name: str) -> Session:
        session = self.repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        return self.repo.update_audit_name(session, audit_name)
