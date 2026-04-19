# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.core.constants import DEFAULT_EVIDENCE_STATUS
from app.models.evidence import EvidenceMetadata
from app.utils.uuid_helper import generate_uuid


class EvidenceRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create(
        self,
        session_id: str,
        filename: str,
        file_ref: str,
        status: str = DEFAULT_EVIDENCE_STATUS,
    ) -> EvidenceMetadata:
        evidence = EvidenceMetadata(
            id=generate_uuid(),
            session_id=session_id,
            filename=filename,
            file_ref=file_ref,
            status=status,
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_by_file_ref(self, file_ref: str) -> Optional[EvidenceMetadata]:
        return (
            self.db.query(EvidenceMetadata)
            .filter(EvidenceMetadata.file_ref == file_ref)
            .first()
        )

    def update_status(
        self,
        evidence: EvidenceMetadata,
        status: str,
        file_ref: Optional[str] = None,
    ) -> EvidenceMetadata:
        evidence.status = status
        if file_ref:
            evidence.file_ref = file_ref
        self.db.commit()
        self.db.refresh(evidence)
        return evidence
