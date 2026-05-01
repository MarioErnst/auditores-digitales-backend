# -*- coding: utf-8 -*-
import hmac

from fastapi import Header, HTTPException

from app.config import settings
from app.utils.logger import log_warning

_api_key_warning_logged = False


async def verify_n8n_webhook(
    x_n8n_secret: str = Header(default=""),
) -> None:
    if not settings.n8n_webhook_secret:
        return  # modo dev: secret no configurado, se permite todo
    if not hmac.compare_digest(x_n8n_secret, settings.n8n_webhook_secret):
        raise HTTPException(status_code=401, detail="Unauthorized")


async def verify_api_key(
    x_api_key: str = Header(default=""),
) -> None:
    global _api_key_warning_logged
    if not settings.api_key:
        if settings.app_env == "development":
            if not _api_key_warning_logged:
                log_warning(
                    "API_KEY no configurada — todos los endpoints sin proteger (app_env=development)"
                )
                _api_key_warning_logged = True
            return
        raise HTTPException(status_code=401, detail="API key no configurada en el servidor")
    if not hmac.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=401, detail="API key inválida o ausente")
