from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from backend.database import get_db
from backend.models import ChatHistory, Session, generate_uuid
from backend.schemas import ChatRequest, ChatResponse, SourceInfo
from backend.utils.n8n import n8n_client

router = APIRouter(prefix="/chat", tags=["chat"])

_N8N_OFFLINE_RESPONSE = "N8N no disponible en este momento"


@router.post("/", response_model=ChatResponse)
def chat(body: ChatRequest, db: DBSession = Depends(get_db)) -> ChatResponse:
    # Validar que la sesión existe
    session = db.query(Session).filter(Session.id == body.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    respuesta = _N8N_OFFLINE_RESPONSE
    fuentes: list[SourceInfo] = []

    try:
        result = n8n_client.trigger_chat(body.pregunta, body.session_id)

        if result.get("status") != "error":
            respuesta = result.get("respuesta", _N8N_OFFLINE_RESPONSE)
            fuentes = [
                SourceInfo(nombre=f.get("nombre", ""), relevancia=f.get("relevancia"))
                for f in result.get("fuentes", [])
            ]
    except Exception as e:
        print(f"⚠️ Chat sin N8N: {e}")

    # Guardar en BD solo si obtuvimos respuesta real
    if respuesta != _N8N_OFFLINE_RESPONSE:
        history = ChatHistory(
            id=generate_uuid(),
            session_id=body.session_id,
            question=body.pregunta,
            answer=respuesta,
            sources=[{"nombre": f.nombre, "relevancia": f.relevancia} for f in fuentes],
        )
        db.add(history)
        db.commit()

    return ChatResponse(
        respuesta=respuesta,
        fuentes=fuentes,
        session_id=body.session_id,
        timestamp=datetime.utcnow(),
    )
