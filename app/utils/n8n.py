# -*- coding: utf-8 -*-
import requests

from app.config import settings
from app.core.exceptions import N8NUnavailableError
from app.utils.logger import log_chat, log_success, log_upload, log_warning

_UPLOAD_TIMEOUT = 30
_CHAT_TIMEOUT = 60


class N8NClient:
    def __init__(self) -> None:
        self.base_url = settings.n8n_base_url

    def trigger_upload(
        self, file_base64: str, filename: str, session_id: str, request_id: str
    ) -> dict:
        url = f"{self.base_url}/webhook-test/upload-evidence"
        payload = {
            "request_id": request_id,
            "file": file_base64,
            "filename": filename,
            "session_id": session_id,
        }

        log_upload(
            f"Disparando N8N upload para {filename} (request_id={request_id})"
        )
        try:
            response = requests.post(url, json=payload, timeout=_UPLOAD_TIMEOUT)
        except requests.Timeout:
            raise N8NUnavailableError("timeout en upload-evidence")
        except requests.RequestException as e:
            raise N8NUnavailableError(str(e))

        if response.status_code not in (200, 202):
            log_warning(f"N8N respondió con status {response.status_code}")
            return {"status": "error", "detail": f"N8N status {response.status_code}"}

        log_success(f"N8N respondió OK para request_id={request_id}")
        try:
            return response.json()
        except Exception:
            log_warning("N8N upload respondió OK pero sin JSON válido")
            return {"status": "ok", "request_id": request_id}

    def trigger_chat(
        self, question: str, session_id: str, request_id: str
    ) -> dict:
        url = f"{self.base_url}/webhook/chat-query"
        payload = {
            "request_id": request_id,
            "question": question,
            "session_id": session_id,
        }

        log_chat(
            f"Disparando N8N chat para session_id={session_id} (request_id={request_id})"
        )
        try:
            response = requests.post(url, json=payload, timeout=_CHAT_TIMEOUT)
        except requests.Timeout:
            raise N8NUnavailableError(f"timeout en chat-query ({_CHAT_TIMEOUT}s)")
        except requests.RequestException as e:
            raise N8NUnavailableError(str(e))

        if response.status_code not in (200, 202):
            log_warning(f"N8N respondió con status {response.status_code}")
            return {"status": "error", "detail": f"N8N status {response.status_code}"}

        log_success(f"N8N respondió OK para request_id={request_id}")
        try:
            return response.json()
        except Exception:
            log_warning("N8N chat respondió OK pero sin JSON válido")
            return {"status": "error", "detail": "respuesta no válida"}


n8n_client = N8NClient()
