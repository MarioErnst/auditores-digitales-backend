# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.security import verify_n8n_webhook
from app.repository.audit_log_repository import AuditLogRepository
from app.schemas.webhook import ChatWebhookPayload, EvidenceWebhookPayload
from app.services.chat_service import ChatService
from app.services.evidence_service import EvidenceService
from app.utils.logger import log_success, log_warning

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/evidence-uploaded", dependencies=[Depends(verify_n8n_webhook)])
def evidence_uploaded(
    payload: EvidenceWebhookPayload, db: DBSession = Depends(get_db)
) -> dict:
    try:
        service = EvidenceService(db)
        service.handle_webhook_response(
            payload.request_id, payload.status, payload.file_ref, payload.document_name, payload.store_name
        )

        audit_repo = AuditLogRepository(db)
        audit_repo.create(
            event_type="evidence_uploaded",
            status=payload.status,
            data={
                "request_id": payload.request_id,
                "session_id": payload.session_id,
                "file_ref": payload.file_ref,
                "error": payload.error,
            },
        )
        log_success(
            f"Webhook evidence recibido: request_id={payload.request_id} "
            f"status={payload.status}"
        )
    except Exception as e:
        log_warning(f"Error procesando webhook evidence: {e}")

    return {"received": True}


@router.post("/chat-response", dependencies=[Depends(verify_n8n_webhook)])
def chat_response(
    payload: ChatWebhookPayload, db: DBSession = Depends(get_db)
) -> dict:
    try:
        service = ChatService(db)
        updated = service.handle_webhook_response(
            payload.request_id, payload.answer, payload.sources
        )
        if not updated:
            log_warning(
                f"ChatHistory no encontrado para request_id={payload.request_id}"
            )

        audit_repo = AuditLogRepository(db)
        audit_repo.create(
            event_type="chat_response",
            status="success",
            data={
                "request_id": payload.request_id,
                "session_id": payload.session_id,
                "sources_count": len(payload.sources),
            },
        )
        log_success(f"Webhook chat recibido: request_id={payload.request_id}")
    except Exception as e:
        log_warning(f"Error procesando webhook chat: {e}")

    return {"received": True}
