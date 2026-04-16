from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from backend.database import get_db
from backend.models import Session, generate_uuid
from backend.schemas import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=201)
def create_session(body: SessionCreate, db: DBSession = Depends(get_db)) -> SessionResponse:
    session = Session(id=generate_uuid(), audit_id=body.audit_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: DBSession = Depends(get_db)) -> SessionResponse:
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session
