"""
導出可能な事実も質問として追加するスクリプト

これらの質問は高優先度として設定され、
「わからない」を選択した場合により詳細な質問に進む
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal, engine
from app.models.models import Question, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def add_derivable_questions():
    """導出可能な結論を質問として追加"""
    db = SessionLocal()

    try:
        # 導出可能な事実（rule 2, 5, 15, 23の結論）を質問として追加
        derivable_questions = [
            {
                "fact_name": "会社がEビザの条件を満たします",
                "question_text": "会社がEビザの条件を満たしますか？",
                "visa_type": "E",
                "priority": 95,  # 非常に高い優先度
            },
            {
                "fact_name": "申請者がEビザの条件を満たします",
                "question_text": "申請者がEビザの条件を満たしますか？",
                "visa_type": "E",
                "priority": 85,  # 高い優先度
            },
            {
                "fact_name": "会社がEビザの投資の条件を満たします",
                "question_text": "会社がEビザの投資（E-2）の条件を満たしますか？",
                "visa_type": "E",
                "priority": 90,  # 非常に高い優先度
            },
            {
                "fact_name": "会社がEビザの貿易の条件を満たします",
                "question_text": "会社がEビザの貿易（E-1）の条件を満たしますか？",
                "visa_type": "E",
                "priority": 90,  # 非常に高い優先度
            },
            {
                "fact_name": "申請者がEビザのマネージャー以上の条件を満たします",
                "question_text": "申請者がEビザのマネージャー以上の条件を満たしますか？",
                "visa_type": "E",
                "priority": 80,
            },
            {
                "fact_name": "申請者がEビザのスタッフの条件を満たします",
                "question_text": "申請者がEビザのスタッフ（専門職）の条件を満たしますか？",
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
                "question_text": "Bビザの申請条件を満たしますか？（ESTAの認証が通る場合）",
                "visa_type": "B",
                "priority": 90,
            },
            {
                "fact_name": "Bビザの申請条件を満たす（ESTAの認証は通らない）",
                "question_text": "Bビザの申請条件を満たしますか？（ESTAの認証が通らない場合）",
                "visa_type": "B",
                "priority": 90,
            },
        ]

        added_count = 0
        updated_count = 0

        for q_data in derivable_questions:
            # Check if question already exists
            existing = db.query(Question).filter(
                Question.fact_name == q_data["fact_name"]
            ).first()

            if existing:
                # Update priority
                existing.priority = q_data["priority"]
                existing.question_text = q_data["question_text"]
                updated_count += 1
                print(f"Updated: {q_data['fact_name']} (priority: {q_data['priority']})")
            else:
                # Add new question
                question = Question(**q_data)
                db.add(question)
                added_count += 1
                print(f"Added: {q_data['fact_name']} (priority: {q_data['priority']})")

        db.commit()
        print(f"\n✅ Complete! Added: {added_count}, Updated: {updated_count}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_derivable_questions()
