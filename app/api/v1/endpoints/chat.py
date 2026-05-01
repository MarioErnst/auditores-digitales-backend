# -*- coding: utf-8 -*-
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import ChatNotFoundError, SessionNotFoundError
from app.core.constants import N8N_OFFLINE_MESSAGE
from app.core.security import verify_api_key
from app.schemas.chat import ChatPollResponse, ChatRequest, ChatSubmitResponse
from app.services.chat_service import ChatService, dispatch_chat_to_n8n

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/", response_model=ChatSubmitResponse, status_code=202)
async def chat(
    body: ChatRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
) -> ChatSubmitResponse:
    service = ChatService(db)
    try:
        response = service.process_chat(body.question, body.session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    background_tasks.add_task(
        dispatch_chat_to_n8n, body.question, body.session_id, response.request_id
    )
    return response


@router.get("/{request_id}", response_model=ChatPollResponse)
def get_chat_status(
    request_id: str, db: DBSession = Depends(get_db)
) -> ChatPollResponse:
    service = ChatService(db)
    try:
        chat = service.get_chat_status(request_id)
    except ChatNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    has_answer = bool(chat.answer) and chat.answer != N8N_OFFLINE_MESSAGE
    if has_answer:
        return ChatPollResponse(status="ready", answer=chat.answer, sources=chat.sources)
    return ChatPollResponse(status="pending")
