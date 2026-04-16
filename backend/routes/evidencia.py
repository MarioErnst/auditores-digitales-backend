import base64
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session as DBSession

from backend.database import get_db
from backend.models import EvidenceMetadata, generate_uuid
from backend.schemas import EvidenceUploadResponse
from backend.utils.n8n import n8n_client

router = APIRouter(prefix="/evidencia", tags=["evidencia"])

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".docx", ".xls", ".doc"}
MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("/", response_model=EvidenceUploadResponse, status_code=202)
async def upload_evidence(
    file: UploadFile,
    session_id: str = Query(...),
    db: DBSession = Depends(get_db),
) -> EvidenceUploadResponse:
    # Validar extensión
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extensión no permitida. Usar: {', '.join(ALLOWED_EXTENSIONS)}")

    # Leer y validar tamaño
    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Archivo supera el límite de 50MB")

    # Convertir a base64 y disparar N8N
    archivo_b64 = base64.b64encode(contents).decode()
    request_id = str(uuid4())

    try:
        result = n8n_client.trigger_upload(archivo_b64, filename, session_id)
        # Usar request_id devuelto por N8N si está disponible
        if isinstance(result, dict) and result.get("request_id"):
            request_id = result["request_id"]
    except Exception as e:
        # N8N offline en desarrollo: continuar igual
        print(f"⚠️ N8N no disponible, guardando en BD de todos modos: {e}")

    # Guardar metadatos en BD
    evidence = EvidenceMetadata(
        id=generate_uuid(),
        session_id=session_id,
        filename=filename,
        file_ref=request_id,
        status="processing",
    )
    db.add(evidence)
    db.commit()

    return EvidenceUploadResponse(
        status="processing",
        session_id=session_id,
        request_id=request_id,
        filename=filename,
    )
