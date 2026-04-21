# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.api.v1.dependencies import get_db
from app.core.exceptions import SessionNotFoundError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(body: ChatRequest, db: DBSession = Depends(get_db)) -> ChatResponse:
    service = ChatService(db)
    try:
        return await service.process_chat(body.question, body.session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
