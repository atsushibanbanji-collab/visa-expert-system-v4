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

    # Add fact and run forward chaining (unless answer is None = "分からない")
    if request_data.answer is not None:
        _current_engine.add_fact(fact_name, request_data.answer)
        _current_engine.forward_chain()
    else:
        # If answer is None ("分からない"), mark as unknown and let the system derive it
        _current_engine.add_unknown_fact(fact_name)

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

    # Return current question
    current_question = _question_history[-1] if _question_history else None

    # Get fact names for questions that should remain (excluding current question)
    # Current question will be re-asked, so we don't keep its fact
    facts_to_keep = set()
    for q_text in _question_history[:-1] if len(_question_history) > 0 else []:
        q = db.query(Question).filter(Question.question_text == q_text).first()
        if q:
            facts_to_keep.add(q.fact_name)

    # Update current question fact
    if current_question:
        question = db.query(Question).filter(Question.question_text == current_question).first()
        _current_question_fact = question.fact_name if question else current_question

    # Keep only the facts from questions in history (before current question)
    # Remove all other facts including derived facts
    facts_snapshot = dict(_current_engine.facts)  # Copy to avoid modification during iteration
    for fact_name in facts_snapshot:
        if fact_name not in facts_to_keep:
            if fact_name in _current_engine.facts:
                del _current_engine.facts[fact_name]
            if fact_name in _current_engine.asked_questions:
                _current_engine.asked_questions.remove(fact_name)

    # Clear derived facts, fired rules, and unknown facts (including cascading rules)
    _current_engine.derived_facts.clear()
    _current_engine.fired_rules.clear()
    _current_engine.unknown_facts.clear()

    # Re-derive facts from remaining known facts (only once)
    _current_engine.forward_chain()

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
