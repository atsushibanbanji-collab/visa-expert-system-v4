"""
Lビザの導出可能質問のpriorityを強制的に更新するマイグレーション
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.models.models import Question


def update_l_visa_priorities():
    """Lビザの導出可能質問のpriorityを更新"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("Lビザ導出可能質問のpriority更新")
        print("=" * 60)

        updates = [
            {
                "fact_name": "申請者がLビザ（Individual）の条件を満たします",
                "question_text": "申請者がLビザ（Individual）の条件を満たしますか？",
                "priority": 90,
            },
            {
                "fact_name": "会社がBlanket Lビザの条件を満たします",
                "question_text": "会社がBlanket Lビザの条件を満たしますか？",
                "priority": 85,
            },
            {
                "fact_name": "申請者がBlanket Lビザの条件を満たします",
                "question_text": "申請者がBlanket Lビザの条件を満たしますか？",
                "priority": 85,
            },
            {
                "fact_name": "Blanket Lビザのマネージャーまたはスタッフの条件を満たします",
                "question_text": "Blanket Lビザのマネージャーまたはスタッフの条件を満たしますか？",
                "priority": 80,
            },
        ]

        updated_count = 0

        for update_data in updates:
            question = db.query(Question).filter(
                Question.fact_name == update_data["fact_name"]
            ).first()

            if question:
                old_priority = question.priority
                old_text = question.question_text

                question.priority = update_data["priority"]
                question.question_text = update_data["question_text"]

                print(f"\n✓ {update_data['fact_name']}")
                print(f"  priority: {old_priority} → {update_data['priority']}")
                print(f"  question_text: {old_text}")
                print(f"              → {update_data['question_text']}")

                updated_count += 1
            else:
                print(f"\n✗ Not found: {update_data['fact_name']}")

        db.commit()

        print("\n" + "=" * 60)
        print(f"更新完了: {updated_count}件")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\nエラー: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting migration: Update L visa question priorities...")
    success = update_l_visa_priorities()
    sys.exit(0 if success else 1)
