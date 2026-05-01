# -*- coding: utf-8 -*-
from typing import Optional

import httpx
from sqlalchemy.orm import Session as DBSession

from app.config import settings
from app.core.constants import (
    ALLOWED_EVIDENCE_EXTENSIONS,
    DEFAULT_EVIDENCE_STATUS,
    MAX_EVIDENCE_SIZE_BYTES,
    MAX_EVIDENCE_SIZE_MB,
)
from app.core.exceptions import (
    EvidenceNotFoundError,
    N8NUnavailableError,
    SessionNotFoundError,
)
from app.models.evidence import EvidenceMetadata
from app.repository.evidence_repository import EvidenceRepository
from app.repository.session_repository import SessionRepository
from app.schemas.evidence import EvidenceListItem, EvidenceUploadResponse
from app.services.n8n_service import n8n_service
from app.utils.logger import log_warning
from app.utils.uuid_helper import generate_uuid
from app.utils.validators import validate_extension, validate_size

_GEMINI_DELETE_URL = "https://generativelanguage.googleapis.com/v1beta/{gemini_resource_name}"


class EvidenceService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.session_repo = SessionRepository(db)

    def list_evidence(self, session_id: str) -> list[EvidenceListItem]:
        session = self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        records = self.evidence_repo.get_by_session_id(session_id)
        return [
            EvidenceListItem(
                id=e.id,
                session_id=e.session_id,
                filename=e.filename,
                gemini_resource_name=e.gemini_resource_name,
                store_name=e.store_name,
                status=e.status,
                gemini_ref=e.gemini_ref,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in records
        ]

    async def upload_evidence(
        self, filename: str, contents: bytes, session_id: str
    ) -> EvidenceUploadResponse:
        session = self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        validate_extension(filename, ALLOWED_EVIDENCE_EXTENSIONS)
        validate_size(len(contents), MAX_EVIDENCE_SIZE_BYTES, MAX_EVIDENCE_SIZE_MB)

        request_id = generate_uuid()

        self.evidence_repo.create(
            session_id=session_id,
            filename=filename,
            gemini_ref=request_id,
            status=DEFAULT_EVIDENCE_STATUS,
        )

        try:
            await n8n_service.dispatch_upload(contents, filename, session_id, request_id)
        except N8NUnavailableError as e:
            log_warning(f"N8N no disponible, guardando en BD de todos modos: {e}")

        return EvidenceUploadResponse(
            status=DEFAULT_EVIDENCE_STATUS,
            session_id=session_id,
            request_id=request_id,
            filename=filename,
        )

    def handle_webhook_response(
        self,
        request_id: str,
        status: str,
        gemini_ref: Optional[str] = None,
        gemini_resource_name: Optional[str] = None,
        store_name: Optional[str] = None,
    ) -> Optional[EvidenceMetadata]:
        evidence = self.evidence_repo.get_by_gemini_ref(request_id)
        if not evidence:
            return None
        self.evidence_repo.update_status(evidence, status, gemini_ref, store_name)
        if gemini_resource_name:
            self.evidence_repo.update_gemini_resource_name(evidence, gemini_resource_name)
        return evidence

    async def delete_evidence(self, evidence_id: str, session_id: str) -> str:
        evidence = self.evidence_repo.get_by_id(evidence_id)
        if not evidence or evidence.session_id != session_id:
            raise EvidenceNotFoundError(evidence_id)

        filename = evidence.filename

        if evidence.gemini_resource_name and settings.gemini_api_key:
            url = _GEMINI_DELETE_URL.format(gemini_resource_name=evidence.gemini_resource_name)
            log_warning(f"Gemini DELETE URL: {url} (gemini_api_key_set={bool(settings.gemini_api_key)})")
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.delete(url, params={"force": "true", "key": settings.gemini_api_key})
                log_warning(f"Gemini DELETE status={response.status_code} body={response.text[:300]}")
            except Exception as e:
                log_warning(f"No se pudo borrar de Gemini (gemini_resource_name={evidence.gemini_resource_name}): {e}")
        else:
            log_warning(f"Gemini DELETE saltado: gemini_resource_name={evidence.gemini_resource_name!r} gemini_api_key_set={bool(settings.gemini_api_key)}")

        self.evidence_repo.delete_by_id(evidence_id)
        return filename
