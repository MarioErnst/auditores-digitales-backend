# -*- coding: utf-8 -*-
import base64
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.core.constants import (
    ALLOWED_EVIDENCE_EXTENSIONS,
    DEFAULT_EVIDENCE_STATUS,
    MAX_EVIDENCE_SIZE_BYTES,
    MAX_EVIDENCE_SIZE_MB,
)
from app.core.exceptions import N8NUnavailableError, SessionNotFoundError
from app.models.evidence import EvidenceMetadata
from app.repository.evidence_repository import EvidenceRepository
from app.repository.session_repository import SessionRepository
from app.schemas.evidence import EvidenceUploadResponse
from app.services.n8n_service import n8n_service
from app.utils.logger import log_warning
from app.utils.uuid_helper import generate_uuid
from app.utils.validators import validate_extension, validate_size


class EvidenceService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.session_repo = SessionRepository(db)

    async def upload_evidence(
        self, filename: str, contents: bytes, session_id: str
    ) -> EvidenceUploadResponse:
        session = self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        validate_extension(filename, ALLOWED_EVIDENCE_EXTENSIONS)
        validate_size(len(contents), MAX_EVIDENCE_SIZE_BYTES, MAX_EVIDENCE_SIZE_MB)

        file_base64 = base64.b64encode(contents).decode()
        request_id = generate_uuid()

        try:
            await n8n_service.dispatch_upload(file_base64, filename, session_id, request_id)
        except N8NUnavailableError as e:
            log_warning(f"N8N no disponible, guardando en BD de todos modos: {e}")

        self.evidence_repo.create(
            session_id=session_id,
            filename=filename,
            file_ref=request_id,
            status=DEFAULT_EVIDENCE_STATUS,
        )

        return EvidenceUploadResponse(
            status=DEFAULT_EVIDENCE_STATUS,
            session_id=session_id,
            request_id=request_id,
            filename=filename,
        )

    def handle_webhook_response(
        self, request_id: str, status: str, file_ref: Optional[str] = None
    ) -> Optional[EvidenceMetadata]:
        evidence = self.evidence_repo.get_by_file_ref(request_id)
        if not evidence:
            return None
        return self.evidence_repo.update_status(evidence, status, file_ref)
