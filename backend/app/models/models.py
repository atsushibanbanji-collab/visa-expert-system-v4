from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Rule(Base):
    """ルールテーブル"""
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String, unique=True, index=True, nullable=False)
    visa_type = Column(String, index=True)  # E, L, B, H-1B, J-1
    conclusion = Column(String, nullable=False)
    conclusion_value = Column(Boolean, default=True)
    operator = Column(String, default="AND")  # AND or OR
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conditions = relationship("Condition", back_populates="rule", cascade="all, delete-orphan")
    history = relationship("RuleHistory", back_populates="rule", cascade="all, delete-orphan")


class Condition(Base):
    """条件テーブル"""
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    fact_name = Column(String, nullable=False)
    expected_value = Column(Boolean, default=True)

    # Relationships
    rule = relationship("Rule", back_populates="conditions")


class Question(Base):
    """質問マスタテーブル"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    fact_name = Column(String, unique=True, index=True, nullable=False)
    question_text = Column(Text, nullable=False)
    visa_type = Column(String, index=True)  # E, L, B, etc.
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RuleHistory(Base):
    """ルール変更履歴テーブル"""
    __tablename__ = "rule_history"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE
    changed_by = Column(String, default="admin")
    changes = Column(JSON)  # Store what was changed
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rule = relationship("Rule", back_populates="history")


class ValidationResult(Base):
    """整合性チェック結果キャッシュ"""
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    visa_type = Column(String)
    validation_type = Column(String)  # contradiction, unreachable, circular
    severity = Column(String)  # error, warning
    message = Column(Text)
    details = Column(JSON)
    checked_at = Column(DateTime, default=datetime.utcnow)
