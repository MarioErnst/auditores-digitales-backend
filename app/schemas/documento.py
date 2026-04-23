# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentoUploadResponse(BaseModel):
    status: str
    filename: str
    descripcion: Optional[str] = None
    store: Optional[str] = None
    timestamp: datetime
