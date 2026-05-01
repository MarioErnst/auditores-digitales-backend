# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    session_id: str
    message: str


class AgentChatResponse(BaseModel):
    answer: str
    session_id: str
    timestamp: Optional[str] = None
