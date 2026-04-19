# -*- coding: utf-8 -*-
from app.utils.n8n import n8n_client


class N8NService:
    """Service layer que encapsula el N8NClient.

    Aquí se agrega la lógica de orquestación (retries, fallbacks, logging
    de dominio), mientras que N8NClient se mantiene como cliente HTTP puro.
    """

    def __init__(self) -> None:
        self.client = n8n_client

    def dispatch_upload(
        self, file_base64: str, filename: str, session_id: str
    ) -> dict:
        return self.client.trigger_upload(file_base64, filename, session_id)

    def dispatch_chat(
        self, question: str, session_id: str, request_id: str
    ) -> dict:
        return self.client.trigger_chat(question, session_id, request_id)


n8n_service = N8NService()
