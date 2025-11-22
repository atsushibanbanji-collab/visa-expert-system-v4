"""
JSONファイルからデータベースにインポート
Renderで実行: python import_db_json.py
"""
import json
from app.models.database import SessionLocal
from app.models.models import Rule, Question, RuleCondition

# JSONファイルを読み込み
with open('database_export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

db = SessionLocal()

try:
    # 既存データを削除
    print("既存データを削除しています...")
    db.query(RuleCondition).delete()
    db.query(Rule).delete()
    db.query(Question).delete()
    db.commit()

    # Questions を挿入
    print(f"{len(data['questions'])}個の質問を挿入しています...")
    for q_data in data['questions']:
        question = Question(
            fact_name=q_data['fact_name'],
            question_text=q_data['question_text'],
            visa_type=q_data['visa_type'],
            priority=q_data['priority']
        )
        db.add(question)
    db.commit()

    # Rules と Conditions を挿入
    print(f"{len(data['rules'])}個のルールを挿入しています...")
    for r_data in data['rules']:
        rule = Rule(
            rule_id=r_data['rule_id'],
            visa_type=r_data['visa_type'],
            conclusion=r_data['conclusion'],
            conclusion_value=r_data['conclusion_value'],
            operator=r_data['operator'],
            priority=r_data['priority']
        )
        db.add(rule)
        db.flush()  # ruleのidを取得するため

        # Conditions を挿入
        for c_data in r_data['conditions']:
            condition = RuleCondition(
                rule_id=rule.id,
                fact_name=c_data['fact_name'],
                expected_value=c_data['expected_value']
            )
            db.add(condition)

    db.commit()
    print(f"\n完了！{len(data['questions'])}個の質問と{len(data['rules'])}個のルールをインポートしました。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    db.rollback()
finally:
    db.close()
