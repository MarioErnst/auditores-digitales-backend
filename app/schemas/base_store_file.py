# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseStoreFileCreate(BaseModel):
    filename: str
    description: Optional[str] = None
    store_name: str


class BaseStoreFileUpdate(BaseModel):
    gemini_resource_name: Optional[str] = None
    status: str


class BaseStoreFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    description: Optional[str] = None
    gemini_resource_name: Optional[str] = None
    store_name: str
    status: str
    created_at: datetime
