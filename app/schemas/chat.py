# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
