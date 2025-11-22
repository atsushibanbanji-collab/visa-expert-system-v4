"""
データベースの内容をSQL形式でエクスポート
"""
from app.models.database import SessionLocal
from app.models.models import Rule, Question

db = SessionLocal()

print("-- Clear existing data")
print("DELETE FROM rule_conditions;")
print("DELETE FROM rules;")
print("DELETE FROM questions;")
print()

# Export Questions
print("-- Questions")
questions = db.query(Question).all()
for q in questions:
    visa_type = f"'{q.visa_type}'" if q.visa_type else "NULL"
    print(f"INSERT INTO questions (fact_name, question_text, visa_type, priority) VALUES ('{q.fact_name}', '{q.question_text.replace(chr(39), chr(39)+chr(39))}', {visa_type}, {q.priority});")

print()

# Export Rules
print("-- Rules")
rules = db.query(Rule).all()
for r in rules:
    visa_type = f"'{r.visa_type}'" if r.visa_type else "NULL"
    print(f"INSERT INTO rules (rule_id, visa_type, conclusion, conclusion_value, operator, priority) VALUES ('{r.rule_id}', {visa_type}, '{r.conclusion}', {str(r.conclusion_value).upper()}, '{r.operator}', {r.priority});")

print()

# Export Rule Conditions
print("-- Rule Conditions")
for r in rules:
    for c in r.conditions:
        print(f"INSERT INTO rule_conditions (rule_id, fact_name, expected_value) SELECT id, '{c.fact_name}', {str(c.expected_value).upper()} FROM rules WHERE rule_id = '{r.rule_id}';")

db.close()
