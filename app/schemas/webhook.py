# -*- coding: utf-8 -*-
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.chat import SourceInfo


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
