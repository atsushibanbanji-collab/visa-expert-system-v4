from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models import schemas
from app.services.inference_engine import InferenceEngine
from app.models.models import Question

router = APIRouter(prefix="/consultation", tags=["consultation"])

# Global state (single user for now)
_current_engine = None
_question_history = []  # List of question texts
_state_snapshots = []  # List of engine state snapshots (parallel to _question_history)
_visa_type = None
_current_question_fact = None


@router.post("/start", response_model=schemas.ConsultationResponse)
async def start_consultation(
    request_data: schemas.StartConsultationRequest,
    db: Session = Depends(get_db),
):
    """診断を開始"""
    global _current_engine, _question_history, _state_snapshots, _visa_type, _current_question_fact

    _visa_type = request_data.visa_type
    _current_engine = InferenceEngine(db, request_data.visa_type)
    _question_history = []
    _state_snapshots = []

    # Save initial snapshot (empty state)
    initial_snapshot = _current_engine.save_snapshot()
    _state_snapshots.append(initial_snapshot)

    # Get first question
    next_question_fact = _current_engine.get_next_question()
    _current_question_fact = next_question_fact
    next_question = None
    is_derivable = True

    if next_question_fact:
        question = db.query(Question).filter(Question.fact_name == next_question_fact).first()
        next_question = question.question_text if question else next_question_fact
        _question_history.append(next_question)
        # 導出可能かチェック
        is_derivable = _current_engine._is_derivable(next_question_fact)

    return schemas.ConsultationResponse(
        next_question=next_question,
        is_derivable=is_derivable,
        conclusions=[],
        is_finished=next_question is None,
        unknown_facts=list(_current_engine.unknown_facts),
        insufficient_info=False,
        missing_critical_info=[]
    )


@router.post("/answer", response_model=schemas.ConsultationResponse)
async def answer_question(
    request_data: schemas.AnswerRequest,
    db: Session = Depends(get_db),
):
    """質問に回答"""
    global _current_engine, _question_history, _state_snapshots, _current_question_fact

    if not _current_engine:
        raise HTTPException(status_code=404, detail="Session not found. Please start consultation first.")

    # Update db session and clear cache to avoid connection pool exhaustion
    _current_engine.db = db
    _current_engine.all_rules = None
    _current_engine.rules_by_conclusion.clear()

    # Get fact name from question text
    question = db.query(Question).filter(Question.question_text == request_data.question).first()
    fact_name = question.fact_name if question else request_data.question

    # Add fact and run forward chaining
    if request_data.answer is not None:
        _current_engine.add_fact(fact_name, request_data.answer)
        _current_engine.forward_chain()
    else:
        # If answer is None ("分からない")
        is_fact_derivable = _current_engine._is_derivable(fact_name)
        if not is_fact_derivable:
            # 導出不可能な質問 → uncertain_factsに追加（後で確定）
            _current_engine.add_uncertain_fact(fact_name, True)
            # まだforward_chainは呼ばない（確定していないので）
        else:
            # 導出可能な質問 → unknown_factsに追加のみ
            _current_engine.add_unknown_fact(fact_name)

    # Save snapshot AFTER answering the question
    snapshot = _current_engine.save_snapshot()
    _state_snapshots.append(snapshot)

    # Get next question
    next_question_fact = _current_engine.get_next_question()
    _current_question_fact = next_question_fact
    next_question = None
    is_derivable = True

    if next_question_fact:
        question = db.query(Question).filter(Question.fact_name == next_question_fact).first()
        next_question = question.question_text if question else next_question_fact
        if next_question not in _question_history:
            _question_history.append(next_question)
        # 導出可能かチェック
        is_derivable = _current_engine._is_derivable(next_question_fact)

    # Check if consultation is finished
    is_finished = _current_engine.is_consultation_finished()

    # If finished, finalize diagnosis with uncertain facts
    if is_finished:
        _current_engine.finalize_diagnosis()

    # Get conclusions
    conclusions = _current_engine.get_conclusions()

    # Check if diagnosis failed due to insufficient information
    goal_achieved = _current_engine.goal in _current_engine.facts and _current_engine.facts[_current_engine.goal]
    insufficient_info = is_finished and not goal_achieved and len(_current_engine.unknown_facts) > 0

    # Get missing critical information (uncertain_facts - 導出不可能な質問で「わからない」と答えたもの)
    # 診断成功・失敗に関わらず、常に取得して表示する
    missing_critical_info = []
    if is_finished:
        # Update db session and clear cache before checking derivability
        _current_engine.db = db
        _current_engine.all_rules = None
        _current_engine.rules_by_conclusion.clear()
        missing_critical_info = _current_engine.get_missing_critical_info()
        print(f"[DEBUG] is_finished={is_finished}")
        print(f"[DEBUG] uncertain_facts={_current_engine.uncertain_facts}")
        print(f"[DEBUG] missing_critical_info={missing_critical_info}")
        print(f"[DEBUG] insufficient_info={insufficient_info}")
        print(f"[DEBUG] conclusions={conclusions}")

    return schemas.ConsultationResponse(
        next_question=next_question,
        is_derivable=is_derivable,
        conclusions=conclusions,
        is_finished=is_finished,
        unknown_facts=list(_current_engine.unknown_facts),
        insufficient_info=insufficient_info,
        missing_critical_info=missing_critical_info
    )


@router.post("/back")
async def go_back(db: Session = Depends(get_db)):
    """前の質問に戻る"""
    global _current_engine, _question_history, _state_snapshots, _current_question_fact

    if not _current_engine:
        raise HTTPException(status_code=404, detail="Session not found. Please start consultation first.")

    if len(_question_history) <= 1:
        # Already at first question or no questions yet
        current_question = _question_history[0] if _question_history else None
        if current_question:
            question = db.query(Question).filter(Question.question_text == current_question).first()
            _current_question_fact = question.fact_name if question else current_question
        
        # Restore to initial state (first snapshot)
        if _state_snapshots:
            _current_engine.restore_snapshot(_state_snapshots[0])
            # Update db session after restoration
            _current_engine.db = db
            _current_engine.all_rules = None
            _current_engine.rules_by_conclusion.clear()
        
        return {"current_question": current_question}

    # Remove last question and its snapshot
    _question_history.pop()
    _state_snapshots.pop()

    # Get current question (now the last one in history)
    current_question = _question_history[-1] if _question_history else None

    # Restore engine state from the last snapshot
    if _state_snapshots:
        _current_engine.restore_snapshot(_state_snapshots[-1])
        # Update db session after restoration
        _current_engine.db = db
        _current_engine.all_rules = None
        _current_engine.rules_by_conclusion.clear()

    # Update current question fact
    if current_question:
        question = db.query(Question).filter(Question.question_text == current_question).first()
        _current_question_fact = question.fact_name if question else current_question

    return {"current_question": current_question}


@router.get("/visualization", response_model=schemas.VisualizationResponse)
async def get_visualization(db: Session = Depends(get_db)):
    """推論過程の可視化データを取得"""
    global _current_engine, _current_question_fact

    if not _current_engine:
        # Return empty visualization if no session
        return schemas.VisualizationResponse(rules=[], fired_rules=[], current_question_fact=None)

    # Update db session and clear cache to avoid lazy loading issues
    _current_engine.db = db
    _current_engine.all_rules = None
    _current_engine.rules_by_conclusion.clear()

    result = _current_engine.get_rule_visualization()
    result["current_question_fact"] = _current_question_fact
    return schemas.VisualizationResponse(**result)
