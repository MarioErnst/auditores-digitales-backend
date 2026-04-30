# -*- coding: utf-8 -*-
from typing import List, Optional

from sqlalchemy.orm import Session as DBSession

from app.core.constants import CHAT_STATUS_COMPLETED, CHAT_STATUS_PROCESSING
from app.models.chat_history import ChatHistory
from app.utils.uuid_helper import generate_uuid


class ChatRepository:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def create(
        self,
        session_id: str,
        request_id: str,
        question: str,
        status: str = CHAT_STATUS_PROCESSING,
        answer: Optional[str] = None,
        sources: Optional[List[dict]] = None,
    ) -> ChatHistory:
        history = ChatHistory(
            id=generate_uuid(),
            session_id=session_id,
            request_id=request_id,
            question=question,
            answer=answer,
            sources=sources or [],
            status=status,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_by_request_id(self, request_id: str) -> Optional[ChatHistory]:
        return (
            self.db.query(ChatHistory)
            .filter(ChatHistory.request_id == request_id)
            .first()
        )

    def list_by_session(self, session_id: str) -> List[ChatHistory]:
        return (
            self.db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.asc())
            .all()
        )

    def update_answer(
        self, history: ChatHistory, answer: str, sources: List[dict]
    ) -> ChatHistory:
        history.answer = answer
        history.sources = sources
        history.status = CHAT_STATUS_COMPLETED
        self.db.commit()
        self.db.refresh(history)
        return history

    def update_status(self, history: ChatHistory, status: str) -> ChatHistory:
        history.status = status
        self.db.commit()
        self.db.refresh(history)
        return history
