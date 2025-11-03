"""Test backward chaining implementation"""
import sys
sys.path.insert(0, 'C:\\Users\\GPC999\\Documents\\works\\visa-expert-system-v4\\backend')

from app.models.database import SessionLocal
from app.services.inference_engine import InferenceEngine

def test_backward_chaining():
    print("=" * 50)
    print("Testing Backward Chaining Implementation")
    print("=" * 50)

    db = SessionLocal()
    try:
        # Initialize engine
        print("\n1. Initializing InferenceEngine for E visa...")
        engine = InferenceEngine(db, 'E')
        print(f"   Goal: {engine.goal}")

        # Get first question
        print("\n2. Getting first question...")
        question = engine.get_next_question()
        print(f"   First question: {question}")

        if question is None:
            print("   ERROR: No question returned!")
            return False

        # Answer the question
        print("\n3. Answering the question (True)...")
        engine.add_fact(question, True)
        engine.forward_chain()

        # Get next question
        print("\n4. Getting next question...")
        next_question = engine.get_next_question()
        print(f"   Next question: {next_question}")

        # Check conclusions
        print("\n5. Checking conclusions...")
        conclusions = engine.get_conclusions()
        print(f"   Conclusions: {conclusions}")

        print("\n" + "=" * 50)
        print("Test completed successfully!")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_backward_chaining()
    sys.exit(0 if success else 1)
