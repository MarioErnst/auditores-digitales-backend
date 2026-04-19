from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from backend.database import get_db
from backend.models import ChatHistory, Session, generate_uuid
from backend.schemas import ChatRequest, ChatResponse, SourceInfo
from backend.utils.n8n import n8n_client

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def chat(body: ChatRequest, db: DBSession = Depends(get_db)) -> ChatResponse:
    session = db.query(Session).filter(Session.id == body.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    request_id = generate_uuid()

    history = ChatHistory(
        id=generate_uuid(),
        session_id=body.session_id,
        request_id=request_id,
        question=body.question,
        answer=None,
        sources=[],
    )
    db.add(history)
    db.commit()

    answer: str | None = None
    sources: list[SourceInfo] = []

    try:
        result = n8n_client.trigger_chat(body.question, body.session_id, request_id)
        if result.get("status") != "error":
            answer = result.get("answer") or result.get("respuesta")
            raw_sources = result.get("sources") or result.get("fuentes", [])
            sources = [
                SourceInfo.model_validate(f) for f in raw_sources
            ]
            history.answer = answer
            history.sources = [{"name": f.name, "relevance": f.relevance} for f in sources]
            db.commit()
    except Exception as e:
        print(f"⚠️ Chat sin N8N: {e}")

    return ChatResponse(
        answer=answer or "N8N no disponible en este momento",
        sources=sources,
        session_id=body.session_id,
        request_id=request_id,
        timestamp=datetime.utcnow(),
    )
