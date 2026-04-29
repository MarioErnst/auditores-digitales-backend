# -*- coding: utf-8 -*-
from typing import List, Optional

from sqlalchemy.orm import Session as DBSession

from app.core.constants import CHAT_STATUS_ERROR, CHAT_STATUS_PROCESSING
from app.core.exceptions import ChatNotFoundError, N8NUnavailableError, SessionNotFoundError
from app.database import SessionLocal
from app.models.chat_history import ChatHistory
from app.repository.chat_repository import ChatRepository
from app.repository.session_repository import SessionRepository
from app.schemas.chat import ChatStatusResponse, ChatSubmitResponse, SourceInfo
from app.services.n8n_service import n8n_service
from app.utils.logger import log_warning
from app.utils.uuid_helper import generate_uuid


async def dispatch_chat_to_n8n(question: str, session_id: str, request_id: str) -> None:
    """Background task: llama a N8N y marca error si no responde."""
    db = SessionLocal()
    try:
        await n8n_service.dispatch_chat(question, session_id, request_id)
    except N8NUnavailableError as e:
        log_warning(f"N8N no disponible para chat (request_id={request_id}): {e}")
        repo = ChatRepository(db)
        history = repo.get_by_request_id(request_id)
        if history:
            repo.update_status(history, CHAT_STATUS_ERROR)
    finally:
        db.close()


class ChatService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.session_repo = SessionRepository(db)

    def process_chat(self, question: str, session_id: str) -> ChatSubmitResponse:
        session = self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        request_id = generate_uuid()

        self.chat_repo.create(
            session_id=session_id,
            request_id=request_id,
            question=question,
            status=CHAT_STATUS_PROCESSING,
        )

        return ChatSubmitResponse(
            request_id=request_id,
            session_id=session_id,
            status=CHAT_STATUS_PROCESSING,
        )

    def get_chat_status(self, request_id: str) -> ChatStatusResponse:
        history = self.chat_repo.get_by_request_id(request_id)
        if not history:
            raise ChatNotFoundError(request_id)

        sources = [SourceInfo.model_validate(s) for s in (history.sources or [])]

        return ChatStatusResponse(
            request_id=history.request_id,
            session_id=history.session_id,
            status=history.status,
            question=history.question,
            answer=history.answer,
            sources=sources,
            timestamp=history.created_at,
        )

    def handle_webhook_response(
        self, request_id: str, answer: str, sources: List[SourceInfo]
    ) -> Optional[ChatHistory]:
        history = self.chat_repo.get_by_request_id(request_id)
        if not history:
            return None
        sources_json = [s.model_dump(exclude_none=True) for s in sources]
        return self.chat_repo.update_answer(history, answer, sources_json)
