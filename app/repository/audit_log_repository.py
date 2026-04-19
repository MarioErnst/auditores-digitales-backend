# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.audit_log import AuditLog
from app.utils.uuid_helper import generate_uuid


class AuditLogRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create(
        self,
        event_type: str,
        status: str,
        data: Optional[dict] = None,
    ) -> AuditLog:
        log = AuditLog(
            id=generate_uuid(),
            event_type=event_type,
            status=status,
            data=data or {},
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
