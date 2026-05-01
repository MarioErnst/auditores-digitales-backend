# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentoUploadResponse(BaseModel):
    status: str
    filename: str
    description: Optional[str] = None
    store: Optional[str] = None
    gemini_resource_name: Optional[str] = None
    file_id: Optional[UUID] = None
    timestamp: datetime
