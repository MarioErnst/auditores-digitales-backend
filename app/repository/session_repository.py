# -*- coding: utf-8 -*-
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.models.evidence import EvidenceMetadata
from app.models.session import Session
from app.utils.uuid_helper import generate_uuid


class SessionRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create(self, audit_name: str, audit_id: Optional[str] = None) -> Session:
        session = Session(id=generate_uuid(), audit_id=audit_id, audit_name=audit_name)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get(self, session_id: str) -> Optional[Session]:
        return self.db.query(Session).filter(Session.id == session_id).first()

    def list_all(self) -> List[tuple]:
        return (
            self.db.query(
                Session,
                func.count(EvidenceMetadata.id).label("evidencias_count"),
            )
            .outerjoin(EvidenceMetadata, EvidenceMetadata.session_id == Session.id)
            .group_by(Session.id)
            .order_by(Session.created_at.desc())
            .all()
        )

    def update_audit_name(self, session: Session, audit_name: str) -> Session:
        session.audit_name = audit_name
        self.db.commit()
        self.db.refresh(session)
        return session
