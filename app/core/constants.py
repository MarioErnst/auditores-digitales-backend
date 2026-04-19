# -*- coding: utf-8 -*-

ALLOWED_EVIDENCE_EXTENSIONS: set[str] = {".pdf", ".xlsx", ".docx", ".xls", ".doc"}
MAX_EVIDENCE_SIZE_MB: int = 50
MAX_EVIDENCE_SIZE_BYTES: int = MAX_EVIDENCE_SIZE_MB * 1024 * 1024

N8N_OFFLINE_MESSAGE: str = "N8N no disponible en este momento"

DEFAULT_SESSION_STATUS: str = "active"
DEFAULT_EVIDENCE_STATUS: str = "processing"
