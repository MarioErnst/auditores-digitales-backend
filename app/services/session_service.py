# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.core.exceptions import SessionNotFoundError
from app.models.session import Session
from app.repository.session_repository import SessionRepository


class SessionService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.repo = SessionRepository(db)

    def create_session(self, audit_id: Optional[str] = None) -> Session:
        return self.repo.create(audit_id=audit_id)


    def list_sessions(self):
        return self.repo.list_all()
    def get_session(self, session_id: str) -> Session:
        session = self.repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        return session

    def get_session_or_none(self, session_id: str) -> Optional[Session]:
        return self.repo.get(session_id)
