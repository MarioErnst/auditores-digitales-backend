# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SessionCreate(BaseModel):
    audit_id: Optional[str] = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    audit_id: Optional[str]
    created_at: datetime
    status: str
