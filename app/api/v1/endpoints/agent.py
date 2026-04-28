# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import N8NUnavailableError
from app.repository.chat_repository import ChatRepository
from app.repository.session_repository import SessionRepository
from app.utils.logger import log_warning
from app.utils.n8n import n8n_client
from app.utils.uuid_helper import generate_uuid

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    mensaje: str = Field(..., min_length=1)


class AgentChatResponse(BaseModel):
    respuesta: str
    session_id: str
    timestamp: str | None = None


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    body: AgentChatRequest, db: DBSession = Depends(get_db)
) -> AgentChatResponse:
    session_repo = SessionRepository(db)
    if not session_repo.get(body.session_id):
        raise HTTPException(
            status_code=404, detail=f"Sesion {body.session_id} no existe"
        )

    chat_repo = ChatRepository(db)
    request_id = generate_uuid()
    history = chat_repo.create(
        session_id=body.session_id,
        request_id=request_id,
        question=body.mensaje,
    )

    try:
        result = await n8n_client.trigger_agent(
            mensaje=body.mensaje, session_id=body.session_id
        )
    except N8NUnavailableError as e:
        chat_repo.update_answer(history, answer=f"[ERROR] {e}", sources=[])
        raise HTTPException(status_code=503, detail=f"Orquestador no disponible: {e}")

    if result.get("status") == "error":
        detail = result.get("detail", "Error en orquestador")
        chat_repo.update_answer(history, answer=f"[ERROR] {detail}", sources=[])
        raise HTTPException(status_code=502, detail=detail)

    answer = result.get("respuesta", "")
    try:
        chat_repo.update_answer(history, answer=answer, sources=[])
    except Exception as e:
        log_warning(f"No se pudo persistir respuesta en chat_history: {e}")

    return AgentChatResponse(
        respuesta=answer,
        session_id=result.get("session_id", body.session_id),
        timestamp=result.get("timestamp"),
    )
