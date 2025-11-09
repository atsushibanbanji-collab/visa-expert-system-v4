from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Rule, Condition, Question, RuleHistory
from app.models import schemas
from datetime import datetime


class AdminService:
    """管理機能サービス"""

    def __init__(self, db: Session):
        self.db = db

    # ========== Rule Management ==========

    def get_rules(self, visa_type: Optional[str] = None) -> List[Rule]:
        """Get all rules, optionally filtered by visa type"""
        query = self.db.query(Rule)
        if visa_type:
            query = query.filter(Rule.visa_type == visa_type)
        return query.order_by(Rule.priority.desc(), Rule.id).all()

    def get_rule(self, rule_id: int) -> Optional[Rule]:
        """Get rule by ID"""
        return self.db.query(Rule).filter(Rule.id == rule_id).first()

    def create_rule(self, rule_data: schemas.RuleCreate, changed_by: str = "admin") -> Rule:
        """Create new rule"""
        # Create rule
        rule = Rule(
            rule_id=rule_data.rule_id,
            visa_type=rule_data.visa_type,
            conclusion=rule_data.conclusion,
            conclusion_value=rule_data.conclusion_value,
            operator=rule_data.operator,
            priority=rule_data.priority,
            is_final_conclusion=rule_data.is_final_conclusion,
        )
        self.db.add(rule)
        self.db.flush()  # Get rule.id

        # Create conditions
        for cond_data in rule_data.conditions:
            condition = Condition(
                rule_id=rule.id,
                fact_name=cond_data.fact_name,
                expected_value=cond_data.expected_value,
            )
            self.db.add(condition)

        # Log history
        history = RuleHistory(
            rule_id=rule.id,
            action="CREATE",
            changed_by=changed_by,
            changes=rule_data.model_dump(),
        )
        self.db.add(history)

        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule(
        self, rule_id: int, rule_data: schemas.RuleUpdate, changed_by: str = "admin"
    ) -> Optional[Rule]:
        """Update existing rule"""
        rule = self.db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            return None

        # Track changes
        changes = {}

        # Update rule fields
        if rule_data.rule_id is not None and rule_data.rule_id != rule.rule_id:
            changes["rule_id"] = {"old": rule.rule_id, "new": rule_data.rule_id}
            rule.rule_id = rule_data.rule_id

        if rule_data.visa_type is not None and rule_data.visa_type != rule.visa_type:
            changes["visa_type"] = {"old": rule.visa_type, "new": rule_data.visa_type}
            rule.visa_type = rule_data.visa_type

        if rule_data.conclusion is not None and rule_data.conclusion != rule.conclusion:
            changes["conclusion"] = {"old": rule.conclusion, "new": rule_data.conclusion}
            rule.conclusion = rule_data.conclusion

        if rule_data.conclusion_value is not None and rule_data.conclusion_value != rule.conclusion_value:
            changes["conclusion_value"] = {"old": rule.conclusion_value, "new": rule_data.conclusion_value}
            rule.conclusion_value = rule_data.conclusion_value

        if rule_data.operator is not None and rule_data.operator != rule.operator:
            changes["operator"] = {"old": rule.operator, "new": rule_data.operator}
            rule.operator = rule_data.operator

        if rule_data.priority is not None and rule_data.priority != rule.priority:
            changes["priority"] = {"old": rule.priority, "new": rule_data.priority}
            rule.priority = rule_data.priority

        if rule_data.is_final_conclusion is not None and rule_data.is_final_conclusion != rule.is_final_conclusion:
            changes["is_final_conclusion"] = {"old": rule.is_final_conclusion, "new": rule_data.is_final_conclusion}
            rule.is_final_conclusion = rule_data.is_final_conclusion

        # Update conditions if provided
        if rule_data.conditions is not None:
            # Delete old conditions
            self.db.query(Condition).filter(Condition.rule_id == rule_id).delete()

            # Add new conditions
            for cond_data in rule_data.conditions:
                condition = Condition(
                    rule_id=rule.id,
                    fact_name=cond_data.fact_name,
                    expected_value=cond_data.expected_value,
                )
                self.db.add(condition)

            changes["conditions"] = "updated"

        rule.updated_at = datetime.utcnow()

        # Log history
        if changes:
            history = RuleHistory(
                rule_id=rule.id,
                action="UPDATE",
                changed_by=changed_by,
                changes=changes,
            )
            self.db.add(history)

        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: int, changed_by: str = "admin") -> bool:
        """Delete rule"""
        rule = self.db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            return False

        # Log history before deletion
        history = RuleHistory(
            rule_id=rule.id,
            action="DELETE",
            changed_by=changed_by,
            changes={"rule_id": rule.rule_id, "conclusion": rule.conclusion},
        )
        self.db.add(history)
        self.db.commit()

        # Delete rule (cascade will delete conditions and history)
        self.db.delete(rule)
        self.db.commit()
        return True

    def get_rule_history(self, rule_id: int) -> List[RuleHistory]:
        """Get change history for a rule"""
        return (
            self.db.query(RuleHistory)
            .filter(RuleHistory.rule_id == rule_id)
            .order_by(RuleHistory.timestamp.desc())
            .all()
        )

    # ========== Question Management ==========

    def get_questions(self, visa_type: Optional[str] = None) -> List[Question]:
        """Get all questions, optionally filtered by visa type"""
        query = self.db.query(Question)
        if visa_type:
            query = query.filter(Question.visa_type == visa_type)
        return query.order_by(Question.priority.desc(), Question.id).all()

    def get_question(self, question_id: int) -> Optional[Question]:
        """Get question by ID"""
        return self.db.query(Question).filter(Question.id == question_id).first()

    def create_question(self, question_data: schemas.QuestionCreate) -> Question:
        """Create new question"""
        question = Question(
            fact_name=question_data.fact_name,
            question_text=question_data.question_text,
            visa_type=question_data.visa_type,
            priority=question_data.priority,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update_question(
        self, question_id: int, question_data: schemas.QuestionUpdate
    ) -> Optional[Question]:
        """Update existing question"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None

        if question_data.question_text is not None:
            question.question_text = question_data.question_text

        if question_data.visa_type is not None:
            question.visa_type = question_data.visa_type

        if question_data.priority is not None:
            question.priority = question_data.priority

        question.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(question)
        return question

    def delete_question(self, question_id: int) -> bool:
        """Delete question"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return False

        self.db.delete(question)
        self.db.commit()
        return True
