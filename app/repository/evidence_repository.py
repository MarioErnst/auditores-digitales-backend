# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy import desc
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
        gemini_ref: str,
        status: str = DEFAULT_EVIDENCE_STATUS,
    ) -> EvidenceMetadata:
        evidence = EvidenceMetadata(
            id=generate_uuid(),
            session_id=session_id,
            filename=filename,
            gemini_ref=gemini_ref,
            status=status,
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_by_session_id(self, session_id: str) -> list[EvidenceMetadata]:
        return (
            self.db.query(EvidenceMetadata)
            .filter(EvidenceMetadata.session_id == session_id)
            .order_by(desc(EvidenceMetadata.created_at))
            .all()
        )

    def get_by_id(self, evidence_id: str) -> Optional[EvidenceMetadata]:
        return (
            self.db.query(EvidenceMetadata)
            .filter(EvidenceMetadata.id == evidence_id)
            .first()
        )

    def get_by_gemini_ref(self, gemini_ref: str) -> Optional[EvidenceMetadata]:
        return (
            self.db.query(EvidenceMetadata)
            .filter(EvidenceMetadata.gemini_ref == gemini_ref)
            .first()
        )

    def update_status(
        self,
        evidence: EvidenceMetadata,
        status: str,
        gemini_ref: Optional[str] = None,
        store_name: Optional[str] = None,
    ) -> EvidenceMetadata:
        evidence.status = status
        if gemini_ref:
            evidence.gemini_ref = gemini_ref
        if store_name:
            evidence.store_name = store_name
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def update_gemini_resource_name(
        self, evidence: EvidenceMetadata, gemini_resource_name: str
    ) -> EvidenceMetadata:
        evidence.gemini_resource_name = gemini_resource_name
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def delete_by_id(self, evidence_id: str) -> Optional[EvidenceMetadata]:
        evidence = self.get_by_id(evidence_id)
        if not evidence:
            return None
        self.db.delete(evidence)
        self.db.commit()
        return evidence
