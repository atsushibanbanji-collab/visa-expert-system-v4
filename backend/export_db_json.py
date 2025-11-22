"""
データベースの内容をJSON形式でエクスポート
"""
import json
from app.models.database import SessionLocal
from app.models.models import Rule, Question

db = SessionLocal()

# Export Questions
questions = db.query(Question).all()
questions_data = []
for q in questions:
    questions_data.append({
        'fact_name': q.fact_name,
        'question_text': q.question_text,
        'visa_type': q.visa_type,
        'priority': q.priority
    })

# Export Rules and Conditions
rules = db.query(Rule).all()
rules_data = []
for r in rules:
    conditions_data = []
    for c in r.conditions:
        conditions_data.append({
            'fact_name': c.fact_name,
            'expected_value': c.expected_value
        })

    rules_data.append({
        'rule_id': r.rule_id,
        'visa_type': r.visa_type,
        'conclusion': r.conclusion,
        'conclusion_value': r.conclusion_value,
        'operator': r.operator,
        'priority': r.priority,
        'conditions': conditions_data
    })

db.close()

# Save to JSON
data = {
    'questions': questions_data,
    'rules': rules_data
}

with open('database_export.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Exported {len(questions_data)} questions and {len(rules_data)} rules to database_export.json")
