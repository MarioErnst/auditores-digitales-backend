# -*- coding: utf-8 -*-
from typing import Iterable


class ASAIException(Exception):
    """Excepción base del dominio."""


class SessionNotFoundError(ASAIException):
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Sesión no encontrada: {session_id}")


class InvalidFileExtensionError(ASAIException):
    def __init__(self, extension: str, allowed: Iterable[str]) -> None:
        self.extension = extension
        self.allowed = set(allowed)
        super().__init__(
            f"Extensión no permitida: {extension or '(sin extensión)'}. "
            f"Usar: {', '.join(sorted(self.allowed))}"
        )


class FileTooLargeError(ASAIException):
    def __init__(self, max_size_mb: int) -> None:
        self.max_size_mb = max_size_mb
        super().__init__(f"Archivo supera el límite de {max_size_mb}MB")


class N8NUnavailableError(ASAIException):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(f"N8N no disponible: {detail}")


class ChatNotFoundError(ASAIException):
    def __init__(self, request_id: str) -> None:
        self.request_id = request_id
        super().__init__(f"Chat no encontrado: {request_id}")


class EvidenceNotFoundError(ASAIException):
    def __init__(self, evidence_id: str) -> None:
        self.evidence_id = evidence_id
        super().__init__(f"Evidencia no encontrada: {evidence_id}")
