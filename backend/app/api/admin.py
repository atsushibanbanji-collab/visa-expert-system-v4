from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db
from app.models import schemas
from app.services.admin_service import AdminService
from app.services.validation_service import ValidationService
import secrets
import os

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()

# Simple authentication (should be replaced with proper auth in production)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials"""
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ========== Rule Management ==========


@router.get("/rules", response_model=List[schemas.RuleResponse])
async def get_rules(
    visa_type: Optional[str] = None,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Get all rules"""
    service = AdminService(db)
    rules = service.get_rules(visa_type)

    # Convert to response format
    response = []
    for rule in rules:
        response.append(
            schemas.RuleResponse(
                id=rule.id,
                rule_id=rule.rule_id,
                visa_type=rule.visa_type,
                conclusion=rule.conclusion,
                conclusion_value=rule.conclusion_value,
                operator=rule.operator,
                priority=rule.priority,
                is_final_conclusion=rule.is_final_conclusion if hasattr(rule, 'is_final_conclusion') else False,
                conditions=[
                    {"fact_name": c.fact_name, "expected_value": c.expected_value}
                    for c in rule.conditions
                ],
                created_at=rule.created_at,
                updated_at=rule.updated_at,
            )
        )
    return response


@router.get("/rules/{rule_id}", response_model=schemas.RuleResponse)
async def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Get rule by ID"""
    service = AdminService(db)
    rule = service.get_rule(rule_id)

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return schemas.RuleResponse(
        id=rule.id,
        rule_id=rule.rule_id,
        visa_type=rule.visa_type,
        conclusion=rule.conclusion,
        conclusion_value=rule.conclusion_value,
        operator=rule.operator,
        priority=rule.priority,
        is_final_conclusion=rule.is_final_conclusion if hasattr(rule, 'is_final_conclusion') else False,
        conditions=[
            {"fact_name": c.fact_name, "expected_value": c.expected_value}
            for c in rule.conditions
        ],
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.post("/rules", response_model=schemas.RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: schemas.RuleCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Create new rule"""
    service = AdminService(db)
    rule = service.create_rule(rule_data, changed_by=username)

    return schemas.RuleResponse(
        id=rule.id,
        rule_id=rule.rule_id,
        visa_type=rule.visa_type,
        conclusion=rule.conclusion,
        conclusion_value=rule.conclusion_value,
        operator=rule.operator,
        priority=rule.priority,
        is_final_conclusion=rule.is_final_conclusion if hasattr(rule, 'is_final_conclusion') else False,
        conditions=[
            {"fact_name": c.fact_name, "expected_value": c.expected_value}
            for c in rule.conditions
        ],
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.put("/rules/{rule_id}", response_model=schemas.RuleResponse)
async def update_rule(
    rule_id: int,
    rule_data: schemas.RuleUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Update existing rule"""
    service = AdminService(db)
    rule = service.update_rule(rule_id, rule_data, changed_by=username)

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return schemas.RuleResponse(
        id=rule.id,
        rule_id=rule.rule_id,
        visa_type=rule.visa_type,
        conclusion=rule.conclusion,
        conclusion_value=rule.conclusion_value,
        operator=rule.operator,
        priority=rule.priority,
        is_final_conclusion=rule.is_final_conclusion if hasattr(rule, 'is_final_conclusion') else False,
        conditions=[
            {"fact_name": c.fact_name, "expected_value": c.expected_value}
            for c in rule.conditions
        ],
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Delete rule"""
    service = AdminService(db)
    success = service.delete_rule(rule_id, changed_by=username)

    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")


@router.get("/rules/{rule_id}/history", response_model=List[schemas.RuleHistoryResponse])
async def get_rule_history(
    rule_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Get rule change history"""
    service = AdminService(db)
    history = service.get_rule_history(rule_id)

    return [
        schemas.RuleHistoryResponse(
            id=h.id,
            action=h.action,
            changed_by=h.changed_by,
            changes=h.changes,
            timestamp=h.timestamp,
        )
        for h in history
    ]


# ========== Question Management ==========


@router.get("/questions", response_model=List[schemas.QuestionResponse])
async def get_questions(
    visa_type: Optional[str] = None,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Get all questions"""
    service = AdminService(db)
    questions = service.get_questions(visa_type)
    return questions


@router.get("/questions/{question_id}", response_model=schemas.QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Get question by ID"""
    service = AdminService(db)
    question = service.get_question(question_id)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return question


@router.post("/questions", response_model=schemas.QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Create new question"""
    service = AdminService(db)
    question = service.create_question(question_data)
    return question


@router.put("/questions/{question_id}", response_model=schemas.QuestionResponse)
async def update_question(
    question_id: int,
    question_data: schemas.QuestionUpdate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Update existing question"""
    service = AdminService(db)
    question = service.update_question(question_id, question_data)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Delete question"""
    service = AdminService(db)
    success = service.delete_question(question_id)

    if not success:
        raise HTTPException(status_code=404, detail="Question not found")


# ========== Validation ==========


@router.get("/validate/{visa_type}", response_model=schemas.ValidationResponse)
async def validate_rules(
    visa_type: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """Validate rules for a visa type"""
    service = ValidationService(db)
    result = service.validate_rules(visa_type)
    return result


# ========== Migration ==========


@router.post("/migrate/derivable-questions")
async def migrate_derivable_questions(
    db: Session = Depends(get_db),
    username: str = Depends(verify_admin),
):
    """導出可能な質問を追加するマイグレーション"""
    from app.models.models import Question

    try:
        # 導出可能な事実（rule 2, 5, 15, 23の結論）を質問として追加
        derivable_questions = [
            {
                "fact_name": "会社がEビザの条件を満たします",
                "question_text": "会社がEビザの条件を満たしますか？",
                "visa_type": "E",
                "priority": 95,
            },
            {
                "fact_name": "申請者がEビザの条件を満たします",
                "question_text": "申請者がEビザの条件を満たしますか？",
                "visa_type": "E",
                "priority": 85,
            },
            {
                "fact_name": "会社がEビザの投資の条件を満たします",
                "question_text": "会社がEビザの投資の条件を満たしますか？",
                "visa_type": "E",
                "priority": 90,
            },
            {
                "fact_name": "会社がEビザの貿易の条件を満たします",
                "question_text": "会社がEビザの貿易の条件を満たしますか？",
                "visa_type": "E",
                "priority": 90,
            },
            {
                "fact_name": "申請者がEビザのマネージャー以上の条件を満たします",
                "question_text": "申請者がEビザのマネージャー以上の条件を満たしますか？",
                "visa_type": "E",
                "priority": 80,
            },
            {
                "fact_name": "申請者がEビザのスタッフの条件を満たします",
                "question_text": "申請者がEビザのスタッフの条件を満たしますか？",
                "visa_type": "E",
                "priority": 80,
            },
            {
                "fact_name": "Blanket Lビザのマネージャーまたはスタッフの条件を満たします",
                "question_text": "Blanket Lビザのマネージャーまたはスタッフの条件を満たしますか？",
                "visa_type": "L",
                "priority": 85,
            },
            {
                "fact_name": "Bビザの申請ができます",
                "question_text": "Bビザの申請ができますか？",
                "visa_type": "B",
                "priority": 95,
            },
            {
                "fact_name": "Bビザの申請条件を満たす（ESTAの認証は通る）",
                "question_text": "Bビザの申請条件を満たしますか？（ESTAの認証は通る）",
                "visa_type": "B",
                "priority": 90,
            },
            {
                "fact_name": "Bビザの申請条件を満たす（ESTAの認証は通らない）",
                "question_text": "Bビザの申請条件を満たしますか？（ESTAの認証は通らない）",
                "visa_type": "B",
                "priority": 90,
            },
        ]

        added_count = 0
        updated_count = 0
        skipped_count = 0

        for q_data in derivable_questions:
            # Check if question already exists
            existing = db.query(Question).filter(
                Question.fact_name == q_data["fact_name"]
            ).first()

            if existing:
                # Update only if priority is different
                if existing.priority != q_data["priority"]:
                    existing.priority = q_data["priority"]
                    existing.question_text = q_data["question_text"]
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # Add new question
                question = Question(**q_data)
                db.add(question)
                added_count += 1

        db.commit()

        return {
            "success": True,
            "added": added_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "message": f"Migration complete! Added: {added_count}, Updated: {updated_count}, Skipped: {skipped_count}"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
