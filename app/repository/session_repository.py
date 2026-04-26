# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.utils.uuid_helper import generate_uuid


class SessionRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create(self, audit_id: Optional[str] = None) -> Session:
        session = Session(id=generate_uuid(), audit_id=audit_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session


    def list_all(self):
        return self.db.query(Session).order_by(Session.created_at.desc()).all()
    def get(self, session_id: str) -> Optional[Session]:
        return self.db.query(Session).filter(Session.id == session_id).first()
