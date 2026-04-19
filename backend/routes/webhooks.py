from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from backend.database import get_db
from backend.models import AuditLog, ChatHistory, EvidenceMetadata, generate_uuid
from backend.schemas import ChatWebhookPayload, EvidenceWebhookPayload

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/evidence-uploaded")
def evidence_uploaded(
    payload: EvidenceWebhookPayload, db: DBSession = Depends(get_db)
) -> dict:
    try:
        evidence = (
            db.query(EvidenceMetadata)
            .filter(EvidenceMetadata.file_ref == payload.request_id)
            .first()
        )

        if evidence:
            evidence.status = payload.status
            if payload.file_ref:
                evidence.file_ref = payload.file_ref

        log = AuditLog(
            id=generate_uuid(),
            event_type="evidence_uploaded",
            status=payload.status,
            data={
                "request_id": payload.request_id,
                "session_id": payload.session_id,
                "file_ref": payload.file_ref,
                "error": payload.error,
            },
        )
        db.add(log)
        db.commit()
        print(f"✅ Webhook evidence recibido: request_id={payload.request_id} status={payload.status}")
    except Exception as e:
        print(f"⚠️ Error procesando webhook evidence: {e}")

    return {"received": True}


@router.post("/chat-response")
def chat_response(
    payload: ChatWebhookPayload, db: DBSession = Depends(get_db)
) -> dict:
    try:
        sources_json = [
            {"name": s.name, "relevance": s.relevance} for s in payload.sources
        ]

        history = (
            db.query(ChatHistory)
            .filter(ChatHistory.request_id == payload.request_id)
            .first()
        )

        if history:
            history.answer = payload.answer
            history.sources = sources_json
        else:
            print(f"⚠️ ChatHistory no encontrado para request_id={payload.request_id}")

        log = AuditLog(
            id=generate_uuid(),
            event_type="chat_response",
            status="success",
            data={
                "request_id": payload.request_id,
                "session_id": payload.session_id,
                "sources_count": len(payload.sources),
            },
        )
        db.add(log)
        db.commit()
        print(f"✅ Webhook chat recibido: request_id={payload.request_id}")
    except Exception as e:
        print(f"⚠️ Error procesando webhook chat: {e}")

    return {"received": True}
