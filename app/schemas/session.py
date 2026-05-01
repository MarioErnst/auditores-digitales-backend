# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    audit_id: Optional[str] = None
    audit_name: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    audit_id: Optional[str]
    audit_name: Optional[str] = None
    created_at: datetime
    status: str


class SessionListItem(BaseModel):
    id: str
    audit_name: Optional[str] = None
    created_at: datetime
    evidencias_count: int
    status: Optional[str] = None


class SessionListResponse(BaseModel):
    items: List[SessionListItem]
    total: int


class SessionUpdateRequest(BaseModel):
    audit_name: str


class MessageItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    answer: Optional[str] = None
    status: str
    created_at: datetime


class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]
    total: int
