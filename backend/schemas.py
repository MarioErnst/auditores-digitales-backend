from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    audit_id: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    audit_id: Optional[str]
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str


class EvidenceUploadResponse(BaseModel):
    status: str
    session_id: str
    request_id: str
    filename: str


class ChatRequest(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=1000)
    session_id: str


class SourceInfo(BaseModel):
    nombre: str
    relevancia: Optional[float] = None


class ChatResponse(BaseModel):
    respuesta: str
    fuentes: List[SourceInfo]
    session_id: str
    timestamp: datetime
