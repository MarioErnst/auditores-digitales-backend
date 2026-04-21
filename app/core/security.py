# -*- coding: utf-8 -*-
import hmac

from fastapi import Header, HTTPException

from app.config import settings


async def verify_n8n_webhook(
    x_n8n_secret: str = Header(default=""),
) -> None:
    if not settings.n8n_webhook_secret:
        return  # modo dev: secret no configurado, se permite todo
    if not hmac.compare_digest(x_n8n_secret, settings.n8n_webhook_secret):
        raise HTTPException(status_code=401, detail="Unauthorized")
