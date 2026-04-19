# -*- coding: utf-8 -*-
from pydantic import BaseModel


class EvidenceUploadResponse(BaseModel):
    status: str
    session_id: str
    request_id: str
    filename: str
