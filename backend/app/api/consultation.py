from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models import schemas
from app.services.inference_engine import InferenceEngine
from app.models.models import Question

router = APIRouter(prefix="/consultation", tags=["consultation"])

# Global state (single user for now)
_current_engine = None
_question_history = []
_visa_type = None
_current_question_fact = None


@router.post("/start", response_model=schemas.ConsultationResponse)
async def start_consultation(
    request_data: schemas.StartConsultationRequest,
    db: Session = Depends(get_db),
):
    """診断を開始"""
    global _current_engine, _question_history, _visa_type, _current_question_fact

    _visa_type = request_data.visa_type
    _current_engine = InferenceEngine(db, request_data.visa_type)
    _question_history = []

    # Get first question
    next_question_fact = _current_engine.get_next_question()
    _current_question_fact = next_question_fact
    next_question = None

    if next_question_fact:
        question = db.query(Question).filter(Question.fact_name == next_question_fact).first()
        next_question = question.question_text if question else next_question_fact
        _question_history.append(next_question)

    return schemas.ConsultationResponse(
        next_question=next_question,
        conclusions=[],
        is_finished=next_question is None
    )


@router.post("/answer", response_model=schemas.ConsultationResponse)
async def answer_question(
    request_data: schemas.AnswerRequest,
    db: Session = Depends(get_db),
):
    """質問に回答"""
    global _current_engine, _question_history, _current_question_fact

    if not _current_engine:
        raise HTTPException(status_code=404, detail="Session not found. Please start consultation first.")

    # Get fact name from question text
    question = db.query(Question).filter(Question.question_text == request_data.question).first()
    fact_name = question.fact_name if question else request_data.question

    # Add fact and run forward chaining
    _current_engine.add_fact(fact_name, request_data.answer)
    _current_engine.forward_chain()

    # Get next question
    next_question_fact = _current_engine.get_next_question()
    _current_question_fact = next_question_fact
    next_question = None

    if next_question_fact:
        question = db.query(Question).filter(Question.fact_name == next_question_fact).first()
        next_question = question.question_text if question else next_question_fact
        if next_question not in _question_history:
            _question_history.append(next_question)

    # Get conclusions
    conclusions = _current_engine.get_conclusions()
    is_finished = _current_engine.is_consultation_finished()

    return schemas.ConsultationResponse(
        next_question=next_question,
        conclusions=conclusions,
        is_finished=is_finished
    )


@router.post("/back")
async def go_back(db: Session = Depends(get_db)):
    """前の質問に戻る"""
    global _current_engine, _question_history, _current_question_fact

    if not _current_engine:
        raise HTTPException(status_code=404, detail="Session not found. Please start consultation first.")

    if len(_question_history) <= 1:
        current_question = _question_history[0] if _question_history else None
        if current_question:
            question = db.query(Question).filter(Question.question_text == current_question).first()
            _current_question_fact = question.fact_name if question else current_question
        return {"current_question": current_question}

    # Remove last question
    last_question = _question_history.pop()

    # Get fact name and remove it
    question = db.query(Question).filter(Question.question_text == last_question).first()
    if question:
        _current_engine.remove_fact(question.fact_name)

    # Return current question
    current_question = _question_history[-1] if _question_history else None

    # Update current question fact and remove its fact (so user can answer fresh)
    if current_question:
        question = db.query(Question).filter(Question.question_text == current_question).first()
        _current_question_fact = question.fact_name if question else current_question
        # Remove the current question's fact so visualization shows clean state
        if question and question.fact_name in _current_engine.facts:
            _current_engine.remove_fact(question.fact_name)

    return {"current_question": current_question}


@router.get("/visualization", response_model=schemas.VisualizationResponse)
async def get_visualization():
    """推論過程の可視化データを取得"""
    global _current_engine, _current_question_fact

    if not _current_engine:
        # Return empty visualization if no session
        return schemas.VisualizationResponse(rules=[], fired_rules=[], current_question_fact=None)

    result = _current_engine.get_rule_visualization()
    result["current_question_fact"] = _current_question_fact
    return schemas.VisualizationResponse(**result)
