"""全ての質問に「はい」と答えた場合のフローをテスト"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.services.inference_engine import InferenceEngine
from app.models.models import Question

def get_question_text(db, fact_name):
    """質問テキストを取得"""
    question = db.query(Question).filter(Question.fact_name == fact_name).first()
    return question.question_text if question else fact_name

def test_all_yes():
    """全ての質問に「はい」と答えた場合のテスト"""
    db = SessionLocal()
    engine = InferenceEngine(db, "E")

    print("="*80)
    print("TEST: 全ての質問に「はい」と答える")
    print("="*80)

    step = 1
    max_steps = 30  # 無限ループ防止
    question_list = []

    while step <= max_steps:
        fact_name = engine.get_next_question()

        if not fact_name:
            print(f"\n終了: 質問がなくなりました (Step {step})")
            break

        question_text = get_question_text(db, fact_name)

        # 質問の優先度を取得
        question = db.query(Question).filter(Question.fact_name == fact_name).first()
        priority = question.priority if question else 0
        is_derivable = engine._is_derivable(fact_name)

        question_info = {
            'step': step,
            'question': question_text,
            'fact': fact_name,
            'priority': priority,
            'derivable': is_derivable
        }
        question_list.append(question_info)

        print(f"\nStep {step}: {question_text}")
        print(f"  Priority: {priority}, Derivable: {is_derivable}")

        # 「はい」と答える
        engine.add_fact(fact_name, True)
        engine.forward_chain()

        # 導出された事実を表示
        if engine.derived_facts:
            print(f"  Derived: {len(engine.derived_facts)} facts")

        step += 1

    # 最終状態
    print("\n" + "="*80)
    print("最終状態")
    print("="*80)
    print(f"Total questions: {len(question_list)}")
    print(f"Conclusions: {engine.get_conclusions()}")
    print(f"Is finished: {engine.is_consultation_finished()}")

    # 質問リストをサマリー表示
    print("\n" + "="*80)
    print("質問順序のサマリー")
    print("="*80)
    for q in question_list:
        derivable_mark = "[導出可能]" if q['derivable'] else ""
        print(f"{q['step']:2d}. {q['question']:60s} (P:{q['priority']:2d}) {derivable_mark}")

    db.close()

if __name__ == "__main__":
    try:
        test_all_yes()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
