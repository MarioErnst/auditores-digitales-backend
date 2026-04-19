from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    audit_id: Optional[str] = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    audit_id: Optional[str]
    created_at: datetime
    status: str


class ErrorResponse(BaseModel):
    detail: str


class EvidenceUploadResponse(BaseModel):
    status: str
    session_id: str
    request_id: str
    filename: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: str


class SourceInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., validation_alias="nombre")
    relevance: Optional[float] = Field(None, validation_alias="relevancia")


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    session_id: str
    request_id: str
    timestamp: datetime


class EvidenceWebhookPayload(BaseModel):
    request_id: str
    status: str
    file_ref: Optional[str] = None
    session_id: str
    error: Optional[str] = None


class ChatWebhookPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    request_id: str
    answer: str = Field(..., validation_alias="respuesta")
    sources: List[SourceInfo] = Field(..., validation_alias="fuentes")
    session_id: str
