"""
最終結論を質問として登録している不適切なエントリを削除
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.models.models import Question


def remove_final_conclusion_questions():
    """最終結論を質問として登録しているものを削除"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("最終結論質問の削除")
        print("=" * 60)

        # 最終結論として登録されている質問を削除
        # （中間結論のみを質問とすべき）
        final_conclusion_questions = [
            "Bビザの申請ができます",
        ]

        deleted_count = 0

        for fact_name in final_conclusion_questions:
            question = db.query(Question).filter(
                Question.fact_name == fact_name
            ).first()

            if question:
                print(f"\n削除: {fact_name}")
                print(f"  理由: 最終結論は質問として不適切（中間結論のみを質問とすべき）")
                db.delete(question)
                deleted_count += 1
            else:
                print(f"\nスキップ: {fact_name}（既に存在しない）")

        db.commit()

        print("\n" + "=" * 60)
        print(f"削除完了: {deleted_count}件")
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
    print("Starting migration: Remove final conclusion questions...")
    success = remove_final_conclusion_questions()
    sys.exit(0 if success else 1)
