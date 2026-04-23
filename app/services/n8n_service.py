# -*- coding: utf-8 -*-
from app.utils.n8n import n8n_client


class N8NService:
    """Service layer que encapsula el N8NClient.

    Aquí se agrega la lógica de orquestación (retries, fallbacks, logging
    de dominio), mientras que N8NClient se mantiene como cliente HTTP puro.
    """

    def __init__(self) -> None:
        self.client = n8n_client

    async def dispatch_upload(
        self, file_contents: bytes, filename: str, session_id: str, request_id: str
    ) -> dict:
        return await self.client.trigger_upload(
            file_contents, filename, session_id, request_id
        )

    async def dispatch_chat(
        self, question: str, session_id: str, request_id: str
    ) -> dict:
        return await self.client.trigger_chat(question, session_id, request_id)

    async def dispatch_upload_base(
        self, file_contents: bytes, filename: str, descripcion: str
    ) -> dict:
        return await self.client.trigger_upload_base(file_contents, filename, descripcion)


n8n_service = N8NService()
