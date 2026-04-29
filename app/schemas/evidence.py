# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EvidenceUploadResponse(BaseModel):
    status: str
    session_id: str
    request_id: str
    filename: str


class EvidenceListItem(BaseModel):
    id: str
    session_id: str
    filename: str
    document_name: Optional[str] = None
    store_name: Optional[str] = None
    status: str
    file_ref: Optional[str] = None
    created_at: datetime
