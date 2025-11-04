"""「わからない」を連続で押したときのフローをテスト"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.services.inference_engine import InferenceEngine
from app.models.models import Question

def print_state(engine, step):
    """現在の状態を表示"""
    print(f"\n--- Step {step} ---")
    print(f"Known facts: {len(engine.facts)}")
    print(f"Unknown facts: {engine.unknown_facts}")
    print(f"Derived facts: {engine.derived_facts}")
    print(f"Fired rules: {engine.fired_rules}")

def get_question_text(db, fact_name):
    """質問テキストを取得"""
    question = db.query(Question).filter(Question.fact_name == fact_name).first()
    return question.question_text if question else fact_name

def test_all_unknown():
    """全ての質問に「わからない」と答えた場合のテスト"""
    db = SessionLocal()
    engine = InferenceEngine(db, "E")

    print("="*60)
    print("TEST: 全ての質問に「わからない」と答える")
    print("="*60)

    step = 1
    max_steps = 20  # 無限ループ防止

    while step <= max_steps:
        fact_name = engine.get_next_question()

        if not fact_name:
            print(f"\n終了: 質問がなくなりました (Step {step})")
            break

        question_text = get_question_text(db, fact_name)
        print(f"\nStep {step}: {question_text}")
        print(f"  Fact: {fact_name}")

        # 質問の優先度を表示
        question = db.query(Question).filter(Question.fact_name == fact_name).first()
        if question:
            print(f"  Priority: {question.priority}")
            print(f"  Derivable: {engine._is_derivable(fact_name)}")

        # 「わからない」と答える
        print("  -> Answer: UNKNOWN")
        engine.add_unknown_fact(fact_name)
        engine.forward_chain()

        print_state(engine, step)

        step += 1

    # 最終状態
    print("\n" + "="*60)
    print("最終状態")
    print("="*60)
    print(f"Unknown facts: {engine.unknown_facts}")
    print(f"Conclusions: {engine.get_conclusions()}")
    print(f"Is finished: {engine.is_consultation_finished()}")
    print(f"Missing critical info: {engine.get_missing_critical_info()}")

    db.close()

if __name__ == "__main__":
    try:
        test_all_unknown()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
