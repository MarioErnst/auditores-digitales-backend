# -*- coding: utf-8 -*-
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
