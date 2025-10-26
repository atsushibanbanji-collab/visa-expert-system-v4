from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import get_db
from app.models import schemas
from app.services import consultation_service
import uuid

router = APIRouter(prefix="/consultation", tags=["consultation"])

# Global session ID storage (simplified for now)
_current_session_id = None


def get_or_create_session_id(x_session_id: Optional[str] = Header(None)) -> str:
    """Get or create session ID from header"""
    global _current_session_id
    if x_session_id:
        _current_session_id = x_session_id
        return x_session_id
    if _current_session_id:
        return _current_session_id
    _current_session_id = str(uuid.uuid4())
    return _current_session_id


@router.post("/start", response_model=schemas.ConsultationResponse)
async def start_consultation(
    request_data: schemas.StartConsultationRequest,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_or_create_session_id),
):
    """診断を開始"""
    # Delete existing session if any
    consultation_service.delete_session(session_id)

    # Create new session
    session = consultation_service.create_session(session_id, db, request_data.visa_type)
    result = session.start()

    return schemas.ConsultationResponse(**result)


@router.post("/answer", response_model=schemas.ConsultationResponse)
async def answer_question(
    request_data: schemas.AnswerRequest,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_or_create_session_id),
):
    """質問に回答"""
    session = consultation_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please start consultation first.")

    result = session.answer(request_data.question, request_data.answer)
    return schemas.ConsultationResponse(**result)


@router.post("/back")
async def go_back(
    session_id: str = Depends(get_or_create_session_id),
):
    """前の質問に戻る"""
    session = consultation_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please start consultation first.")

    result = session.back()
    return result


@router.get("/visualization", response_model=schemas.VisualizationResponse)
async def get_visualization(
    session_id: str = Depends(get_or_create_session_id),
):
    """推論過程の可視化データを取得"""
    session = consultation_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please start consultation first.")

    result = session.get_visualization()
    return schemas.VisualizationResponse(**result)
