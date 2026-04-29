# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: str


class SourceInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Nuevo formato N8N
    texto: Optional[str] = None
    store: Optional[str] = None
    pagina: Optional[int] = None
    titulo: Optional[str] = None

    # Formato anterior (compatibilidad)
    name: Optional[str] = Field(None, validation_alias="nombre")
    relevance: Optional[float] = Field(None, validation_alias="relevancia")


class ChatSubmitResponse(BaseModel):
    """Respuesta inmediata al POST /chat. El cliente usa request_id para hacer polling."""

    request_id: str
    session_id: str
    status: str


class ChatStatusResponse(BaseModel):
    """Respuesta del GET /chat/{request_id}. Incluye la respuesta cuando status=completed."""

    request_id: str
    session_id: str
    status: str
    question: str
    answer: Optional[str] = None
    sources: List[SourceInfo] = []
    timestamp: datetime


class ChatPollResponse(BaseModel):
    """Respuesta simplificada para polling del frontend."""

    status: Literal["ready", "pending"]
    answer: Optional[str] = None
    sources: List[SourceInfo] = []
