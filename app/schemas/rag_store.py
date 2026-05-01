# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class RagStoreBase(BaseModel):
    store_name: str
    store_type: Literal["base", "session"]
    description: Optional[str] = None
    session_id: Optional[str] = None


class RagStoreCreate(RagStoreBase):
    pass


class RagStoreResponse(RagStoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_count: int
    created_at: datetime
    updated_at: datetime
