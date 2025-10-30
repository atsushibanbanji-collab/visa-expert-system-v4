from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Consultation Schemas
class StartConsultationRequest(BaseModel):
    visa_type: str = Field(..., description="E, L, B, H-1B, or J-1")


class AnswerRequest(BaseModel):
    question: str
    answer: Optional[bool]  # True=はい, False=いいえ, None=分からない


class ConsultationResponse(BaseModel):
    next_question: Optional[str] = None
    conclusions: List[str] = []
    is_finished: bool = False


class VisualizationCondition(BaseModel):
    fact_name: str
    status: str  # satisfied, not_satisfied, unknown
    is_derivable: bool = False


class VisualizationRule(BaseModel):
    rule_id: str
    conditions: List[VisualizationCondition]
    operator: str
    conclusion: str
    conclusion_derived: bool = False
    is_fired: bool = False
    is_fireable: bool = True


class VisualizationResponse(BaseModel):
    rules: List[VisualizationRule]
    fired_rules: List[str] = []
    current_question_fact: Optional[str] = None


# Admin Schemas
class ConditionCreate(BaseModel):
    fact_name: str
    expected_value: bool = True


class RuleCreate(BaseModel):
    rule_id: str
    visa_type: Optional[str] = None
    conclusion: str
    conclusion_value: bool = True
    operator: str = "AND"
    priority: int = 0
    conditions: List[ConditionCreate]


class RuleUpdate(BaseModel):
    rule_id: Optional[str] = None
    visa_type: Optional[str] = None
    conclusion: Optional[str] = None
    conclusion_value: Optional[bool] = None
    operator: Optional[str] = None
    priority: Optional[int] = None
    conditions: Optional[List[ConditionCreate]] = None


class RuleResponse(BaseModel):
    id: int
    rule_id: str
    visa_type: Optional[str]
    conclusion: str
    conclusion_value: bool
    operator: str
    priority: int
    conditions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    fact_name: str
    question_text: str
    visa_type: Optional[str] = None
    priority: int = 0


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    visa_type: Optional[str] = None
    priority: Optional[int] = None


class QuestionResponse(BaseModel):
    id: int
    fact_name: str
    question_text: str
    visa_type: Optional[str]
    priority: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ValidationIssue(BaseModel):
    severity: str  # error, warning
    validation_type: str  # contradiction, unreachable, circular
    message: str
    details: Dict[str, Any] = {}


class ValidationResponse(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue] = []
    checked_at: datetime


class RuleHistoryResponse(BaseModel):
    id: int
    action: str
    changed_by: str
    changes: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True
