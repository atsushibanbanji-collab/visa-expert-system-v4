"""導出可能な質問のテスト"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.services.inference_engine import InferenceEngine
from app.models.models import Question

def test_derivable_questions():
    """導出可能な質問が正しく動作するかテスト"""
    db = SessionLocal()

    print("\n=== Test 1: E-Visa Consultation ===")
    engine = InferenceEngine(db, "E")

    # 最初の質問を取得
    first_question_fact = engine.get_next_question()
    print(f"\nFirst question fact: {first_question_fact}")

    question = db.query(Question).filter(Question.fact_name == first_question_fact).first()
    if question:
        print(f"Question text: {question.question_text}")
        print(f"Priority: {question.priority}")

        # このfact_nameが導出可能かチェック
        is_derivable = engine._is_derivable(first_question_fact)
        print(f"Is derivable: {is_derivable}")

    print("\n=== Test 2: Answer '分からない' ===")
    # 「わからない」と回答
    engine.add_unknown_fact(first_question_fact)

    # 次の質問（詳細質問）を取得
    second_question_fact = engine.get_next_question()
    print(f"\nSecond question fact (after 'unknown'): {second_question_fact}")

    question2 = db.query(Question).filter(Question.fact_name == second_question_fact).first()
    if question2:
        print(f"Question text: {question2.question_text}")
        print(f"Priority: {question2.priority}")
        is_derivable2 = engine._is_derivable(second_question_fact)
        print(f"Is derivable: {is_derivable2}")

    print("\n=== Test 3: Check Derivable Questions ===")
    # 導出可能な質問が追加されているか確認
    derivable_facts = [
        "会社がEビザの条件を満たします",
        "申請者がEビザの条件を満たします",
        "会社がEビザの投資の条件を満たします",
        "会社がEビザの貿易の条件を満たします",
    ]

    for fact in derivable_facts:
        q = db.query(Question).filter(Question.fact_name == fact).first()
        if q:
            print(f"\n{fact}")
            print(f"  Question: {q.question_text}")
            print(f"  Priority: {q.priority}")
            print(f"  Is derivable: {engine._is_derivable(fact)}")
        else:
            print(f"\nWARNING: Question not found for '{fact}'")

    db.close()

if __name__ == "__main__":
    try:
        test_derivable_questions()
        print("\n\nOK: Tests completed!")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
