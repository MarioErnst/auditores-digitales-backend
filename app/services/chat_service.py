# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session as DBSession

from app.core.constants import N8N_OFFLINE_MESSAGE
from app.core.exceptions import SessionNotFoundError
from app.models.chat_history import ChatHistory
from app.repository.chat_repository import ChatRepository
from app.repository.session_repository import SessionRepository
from app.schemas.chat import ChatResponse, SourceInfo
from app.services.n8n_service import n8n_service
from app.utils.logger import log_warning
from app.utils.uuid_helper import generate_uuid


class ChatService:
    def __init__(self, db: DBSession) -> None:
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.session_repo = SessionRepository(db)

    def process_chat(self, question: str, session_id: str) -> ChatResponse:
        session = self.session_repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        request_id = generate_uuid()

        # Guardar upfront con respuesta vacía — así el webhook puede localizar
        # este registro por request_id cuando N8N termine de procesar
        history = self.chat_repo.create(
            session_id=session_id,
            request_id=request_id,
            question=question,
            answer=None,
            sources=[],
        )

        answer: Optional[str] = None
        sources: List[SourceInfo] = []

        try:
            result = n8n_service.dispatch_chat(question, session_id, request_id)
            if result.get("status") != "error":
                answer = result.get("answer") or result.get("respuesta")
                raw_sources = result.get("sources") or result.get("fuentes", [])
                sources = [SourceInfo.model_validate(s) for s in raw_sources]

                sources_json = [
                    {"name": s.name, "relevance": s.relevance} for s in sources
                ]
                self.chat_repo.update_answer(history, answer or "", sources_json)
        except Exception as e:
            log_warning(f"Chat sin N8N: {e}")

        return ChatResponse(
            answer=answer or N8N_OFFLINE_MESSAGE,
            sources=sources,
            session_id=session_id,
            request_id=request_id,
            timestamp=datetime.utcnow(),
        )

    def handle_webhook_response(
        self, request_id: str, answer: str, sources: List[SourceInfo]
    ) -> Optional[ChatHistory]:
        history = self.chat_repo.get_by_request_id(request_id)
        if not history:
            return None
        sources_json = [
            {"name": s.name, "relevance": s.relevance} for s in sources
        ]
        return self.chat_repo.update_answer(history, answer, sources_json)
