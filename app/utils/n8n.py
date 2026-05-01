# -*- coding: utf-8 -*-
import httpx

from app.config import settings
from app.core.exceptions import N8NUnavailableError
from app.utils.logger import log_chat, log_success, log_upload, log_warning

_UPLOAD_TIMEOUT = 30
_CHAT_TIMEOUT = 60
_HEALTH_TIMEOUT = 5

_MIMETYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".csv": "text/csv",
}


def _detect_mimetype(filename: str) -> str:
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    return _MIMETYPES.get(ext, "application/octet-stream")


class N8NClient:
    def __init__(self) -> None:
        self.base_url = settings.n8n_base_url
        self.mode = settings.n8n_webhook_mode

    def _webhook_url(self, path: str) -> str:
        segment = "webhook-test" if self.mode == "test" else "webhook"
        return f"{self.base_url}/{segment}/{path}"

    async def check_health(self) -> dict:
        base = {"url": self.base_url, "mode": self.mode}

        # 1. Intento primario: GET /healthz
        try:
            async with httpx.AsyncClient(timeout=_HEALTH_TIMEOUT) as client:
                r = await client.get(f"{self.base_url}/healthz")
            if r.status_code == 200:
                log_success(f"N8N proceso OK en {self.base_url}/healthz")
                return {
                    **base,
                    "status": "ok",
                    "process": "ok",
                    "message": "N8N operativo",
                }
            log_warning(f"N8N /healthz respondió {r.status_code}, probando fallback")
        except Exception as e:
            log_warning(f"N8N /healthz no accesible ({e}), probando fallback")

        # 2. Fallback: GET base_url, verificar status < 500
        try:
            async with httpx.AsyncClient(timeout=_HEALTH_TIMEOUT) as client:
                r = await client.get(self.base_url)
            if r.status_code < 500:
                log_success(f"N8N respondió en {self.base_url} (status={r.status_code})")
                return {
                    **base,
                    "status": "ok",
                    "process": "ok",
                    "message": f"N8N operativo (fallback, status={r.status_code})",
                }
            log_warning(f"N8N respondió status {r.status_code}")
            return {
                **base,
                "status": "offline",
                "process": "offline",
                "message": f"N8N respondió status {r.status_code}",
            }
        except Exception as e:
            log_warning(f"N8N offline: {e}")
            return {
                **base,
                "status": "offline",
                "process": "offline",
                "message": f"N8N no responde en {self.base_url}",
            }

    async def trigger_upload(
        self, file_contents: bytes, filename: str, session_id: str, request_id: str
    ) -> dict:
        url = self._webhook_url("upload-evidence")
        mimetype = _detect_mimetype(filename)

        log_upload(
            f"Disparando N8N upload para {filename} (request_id={request_id})"
        )
        try:
            async with httpx.AsyncClient(timeout=_UPLOAD_TIMEOUT) as client:
                response = await client.post(
                    url,
                    files={"file": (filename, file_contents, mimetype)},
                    data={
                        "session_id": session_id,
                        "request_id": request_id,
                        "filename": filename,
                    },
                )
        except httpx.TimeoutException:
            raise N8NUnavailableError("timeout en upload-evidence")
        except httpx.RequestError as e:
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

    async def trigger_upload_base(
        self, file_contents: bytes, filename: str, description: str
    ) -> dict:
        url = self._webhook_url("upload-base")
        mimetype = _detect_mimetype(filename)

        log_upload(f"Disparando N8N upload-base para {filename}")
        try:
            async with httpx.AsyncClient(timeout=_UPLOAD_TIMEOUT) as client:
                response = await client.post(
                    url,
                    files={"file": (filename, file_contents, mimetype)},
                    data={"filename": filename, "description": description},
                )
        except httpx.TimeoutException:
            raise N8NUnavailableError("timeout en upload-base")
        except httpx.RequestError as e:
            raise N8NUnavailableError(str(e))

        if response.status_code not in (200, 202):
            log_warning(f"N8N respondió con status {response.status_code}")
            return {"status": "error", "detail": f"N8N status {response.status_code}"}

        log_success(f"N8N respondió OK para upload-base {filename}")
        try:
            return response.json()
        except Exception:
            log_warning("N8N upload-base respondió OK pero sin JSON válido")
            return {"status": "ok"}

    async def trigger_chat(
        self, question: str, session_id: str, request_id: str
    ) -> dict:
        url = self._webhook_url("chat-query")
        payload = {
            "request_id": request_id,
            "question": question,
            "session_id": session_id,
        }

        log_chat(
            f"Disparando N8N chat para session_id={session_id} (request_id={request_id})"
        )
        try:
            async with httpx.AsyncClient(timeout=_CHAT_TIMEOUT) as client:
                response = await client.post(url, json=payload)
        except httpx.TimeoutException:
            raise N8NUnavailableError(f"timeout en chat-query ({_CHAT_TIMEOUT}s)")
        except httpx.RequestError as e:
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


    async def trigger_agent(self, message: str, session_id: str) -> dict:
        url = self._webhook_url("router")
        try:
            async with httpx.AsyncClient(timeout=_CHAT_TIMEOUT) as client:
                response = await client.post(
                    url,
                    json={"session_id": session_id, "message": message},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise N8NUnavailableError(str(e))


n8n_client = N8NClient()
