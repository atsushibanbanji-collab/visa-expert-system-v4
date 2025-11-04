"""「わからない」を選択したときの詳細フローを確認"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.services.inference_engine import InferenceEngine
from app.models.models import Question

def get_question_info(db, fact_name):
    """質問情報を取得"""
    question = db.query(Question).filter(Question.fact_name == fact_name).first()
    return {
        'text': question.question_text if question else fact_name,
        'priority': question.priority if question else 0
    }

def test_scenario():
    """シナリオテスト：最初の10ステップ"""
    db = SessionLocal()
    engine = InferenceEngine(db, "E")

    print("="*80)
    print("シナリオ1: 最初から「わからない」を選択")
    print("="*80)

    for step in range(1, 11):
        fact_name = engine.get_next_question()

        if not fact_name:
            print(f"\nStep {step}: 終了（質問なし）")
            break

        q_info = get_question_info(db, fact_name)
        is_derivable = engine._is_derivable(fact_name)

        print(f"\nStep {step}:")
        print(f"  質問: {q_info['text']}")
        print(f"  Priority: {q_info['priority']}")
        print(f"  導出可能: {'はい' if is_derivable else 'いいえ'}")
        print(f"  回答: わからない")

        engine.add_unknown_fact(fact_name)
        engine.forward_chain()

    print("\n" + "="*80)
    print("シナリオ2: 最初は「はい」、2番目で「わからない」")
    print("="*80)

    # 新しいエンジン
    engine2 = InferenceEngine(db, "E")

    # Step 1: はい
    fact1 = engine2.get_next_question()
    q1_info = get_question_info(db, fact1)
    print(f"\nStep 1:")
    print(f"  質問: {q1_info['text']}")
    print(f"  Priority: {q1_info['priority']}")
    print(f"  回答: はい")
    engine2.add_fact(fact1, True)
    engine2.forward_chain()

    # Step 2: わからない
    fact2 = engine2.get_next_question()
    if fact2:
        q2_info = get_question_info(db, fact2)
        is_derivable2 = engine2._is_derivable(fact2)
        print(f"\nStep 2:")
        print(f"  質問: {q2_info['text']}")
        print(f"  Priority: {q2_info['priority']}")
        print(f"  導出可能: {'はい' if is_derivable2 else 'いいえ'}")
        print(f"  回答: わからない")
        engine2.add_unknown_fact(fact2)
        engine2.forward_chain()

        # Step 3: 次は何が来る？
        fact3 = engine2.get_next_question()
        if fact3:
            q3_info = get_question_info(db, fact3)
            is_derivable3 = engine2._is_derivable(fact3)
            print(f"\nStep 3:")
            print(f"  質問: {q3_info['text']}")
            print(f"  Priority: {q3_info['priority']}")
            print(f"  導出可能: {'はい' if is_derivable3 else 'いいえ'}")

    print("\n" + "="*80)
    print("シナリオ3: 2番目で「はい」")
    print("="*80)

    # 新しいエンジン
    engine3 = InferenceEngine(db, "E")

    # Step 1: はい
    fact1 = engine3.get_next_question()
    q1_info = get_question_info(db, fact1)
    print(f"\nStep 1:")
    print(f"  質問: {q1_info['text']}")
    print(f"  回答: はい")
    engine3.add_fact(fact1, True)
    engine3.forward_chain()

    # Step 2: はい
    fact2 = engine3.get_next_question()
    if fact2:
        q2_info = get_question_info(db, fact2)
        is_derivable2 = engine3._is_derivable(fact2)
        print(f"\nStep 2:")
        print(f"  質問: {q2_info['text']}")
        print(f"  Priority: {q2_info['priority']}")
        print(f"  導出可能: {'はい' if is_derivable2 else 'いいえ'}")
        print(f"  回答: はい")
        engine3.add_fact(fact2, True)
        engine3.forward_chain()

        # Step 3: 次は何が来る？
        fact3 = engine3.get_next_question()
        if fact3:
            q3_info = get_question_info(db, fact3)
            is_derivable3 = engine3._is_derivable(fact3)
            print(f"\nStep 3:")
            print(f"  質問: {q3_info['text']}")
            print(f"  Priority: {q3_info['priority']}")
            print(f"  導出可能: {'はい' if is_derivable3 else 'いいえ'}")

    db.close()

if __name__ == "__main__":
    try:
        test_scenario()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
