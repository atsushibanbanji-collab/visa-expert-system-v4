"""実際の診断フローのテスト"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.services.inference_engine import InferenceEngine
from app.models.models import Question

def print_question(db, fact_name, step):
    """質問を表示"""
    question = db.query(Question).filter(Question.fact_name == fact_name).first()
    question_text = question.question_text if question else fact_name
    priority = question.priority if question else 0
    is_derivable = len(db.query(Question).filter(Question.fact_name == fact_name).all()) > 0

    print(f"\nStep {step}: {question_text}")
    print(f"  - Priority: {priority}")
    print(f"  - Derivable: {is_derivable}")
    return question_text

def test_workflow_with_knowledge():
    """知識がある人の診断フロー"""
    print("\n" + "="*60)
    print("TEST CASE 1: User has high-level knowledge")
    print("="*60)

    db = SessionLocal()
    engine = InferenceEngine(db, "E")

    # Step 1: Get first question
    fact = engine.get_next_question()
    print_question(db, fact, 1)

    # Step 2: Answer the first question (basic fact)
    print("\n  -> Answering: Yes")
    engine.add_fact(fact, True)
    engine.forward_chain()

    # Step 3: Get next question (should be derivable high-level question)
    fact = engine.get_next_question()
    if fact:
        print_question(db, fact, 2)

        # Step 4: Answer with high-level knowledge
        print("\n  -> User knows the answer: Yes")
        engine.add_fact(fact, True)
        engine.forward_chain()

        # Step 5: Get next question
        fact = engine.get_next_question()
        if fact:
            print_question(db, fact, 3)

    db.close()

def test_workflow_without_knowledge():
    """知識がない人の診断フロー"""
    print("\n" + "="*60)
    print("TEST CASE 2: User doesn't have high-level knowledge")
    print("="*60)

    db = SessionLocal()
    engine = InferenceEngine(db, "E")

    # Step 1: Get first question
    fact = engine.get_next_question()
    print_question(db, fact, 1)

    # Step 2: Answer the first question
    print("\n  -> Answering: Yes")
    engine.add_fact(fact, True)
    engine.forward_chain()

    # Step 3: Get next question (derivable)
    fact = engine.get_next_question()
    if fact:
        print_question(db, fact, 2)

        # Step 4: User doesn't know the answer
        print("\n  -> User doesn't know the answer: Unknown")
        engine.add_unknown_fact(fact)

        # Step 5: Get detailed question
        fact = engine.get_next_question()
        if fact:
            print_question(db, fact, 3)
            print("\n  -> This should be a more detailed question!")

            # Step 6: Answer detailed question
            print("\n  -> Answering detailed question: Yes")
            engine.add_fact(fact, True)
            engine.forward_chain()

            # Step 7: Get next question
            fact = engine.get_next_question()
            if fact:
                print_question(db, fact, 4)

    db.close()

def test_first_questions_are_derivable():
    """最初の質問が導出可能な高レベル質問かテスト"""
    print("\n" + "="*60)
    print("TEST CASE 3: Check if high-priority derivable questions come first")
    print("="*60)

    db = SessionLocal()

    # Test for E-Visa
    print("\nE-Visa first 5 questions:")
    engine = InferenceEngine(db, "E")

    for i in range(5):
        fact = engine.get_next_question()
        if not fact:
            break

        question = db.query(Question).filter(Question.fact_name == fact).first()
        question_text = question.question_text[:50] + "..." if question and len(question.question_text) > 50 else (question.question_text if question else fact)
        priority = question.priority if question else 0
        is_derivable = engine._is_derivable(fact)

        print(f"\n{i+1}. {question_text}")
        print(f"   Priority: {priority}, Derivable: {is_derivable}")

        # Answer to proceed
        if i < 4:  # Don't answer the last one
            engine.add_fact(fact, True)
            engine.forward_chain()

    db.close()

if __name__ == "__main__":
    try:
        test_workflow_with_knowledge()
        test_workflow_without_knowledge()
        test_first_questions_are_derivable()
        print("\n\n" + "="*60)
        print("OK: All workflow tests completed!")
        print("="*60)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
