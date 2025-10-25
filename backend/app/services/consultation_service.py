from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.services.inference_engine import InferenceEngine
from app.models.models import Question


class ConsultationSession:
    """診断セッション管理"""

    def __init__(self, session_id: str, db: Session, visa_type: str):
        self.session_id = session_id
        self.db = db
        self.visa_type = visa_type
        self.engine = InferenceEngine(db, visa_type)
        self.question_history = []  # Track questions in order

    def start(self) -> Dict:
        """診断を開始"""
        next_question = self._get_next_question_text()
        if next_question:
            self.question_history.append(next_question)

        return {
            "next_question": next_question,
            "conclusions": [],
            "is_finished": next_question is None,
        }

    def answer(self, question_text: str, answer: bool) -> Dict:
        """質問に回答"""
        # Get fact name from question text
        fact_name = self._get_fact_name_from_question(question_text)

        if fact_name:
            self.engine.add_fact(fact_name, answer)
            self.engine.forward_chain()

        # Get next question
        next_question = self._get_next_question_text()
        if next_question and next_question not in self.question_history:
            self.question_history.append(next_question)

        conclusions = self.engine.get_conclusions()
        is_finished = self.engine.is_consultation_finished()

        return {
            "next_question": next_question,
            "conclusions": conclusions,
            "is_finished": is_finished,
        }

    def back(self) -> Dict:
        """前の質問に戻る"""
        if len(self.question_history) <= 1:
            return {"current_question": self.question_history[0] if self.question_history else None}

        # Remove last question from history
        last_question = self.question_history.pop()

        # Get fact name and remove it
        fact_name = self._get_fact_name_from_question(last_question)
        if fact_name:
            self.engine.remove_fact(fact_name)
            self.engine.forward_chain()

        # Return current question
        current_question = self.question_history[-1] if self.question_history else None

        return {"current_question": current_question}

    def get_visualization(self) -> Dict:
        """推論過程の可視化データを取得"""
        return self.engine.get_rule_visualization()

    def _get_next_question_text(self) -> Optional[str]:
        """次の質問のテキストを取得"""
        fact_name = self.engine.get_next_question()
        if not fact_name:
            return None

        question = self.db.query(Question).filter(Question.fact_name == fact_name).first()

        if question:
            return question.question_text
        else:
            # Fallback to fact name if no question defined
            return fact_name

    def _get_fact_name_from_question(self, question_text: str) -> Optional[str]:
        """質問文からfact_nameを取得"""
        question = self.db.query(Question).filter(Question.question_text == question_text).first()
        return question.fact_name if question else question_text


# Global session storage (in-memory for now)
# TODO: Upgrade to Redis or database-backed sessions for production
_sessions: Dict[str, ConsultationSession] = {}


def get_session(session_id: str) -> Optional[ConsultationSession]:
    """Get existing session"""
    return _sessions.get(session_id)


def create_session(session_id: str, db: Session, visa_type: str) -> ConsultationSession:
    """Create new consultation session"""
    session = ConsultationSession(session_id, db, visa_type)
    _sessions[session_id] = session
    return session


def delete_session(session_id: str):
    """Delete consultation session"""
    if session_id in _sessions:
        del _sessions[session_id]
