"""
Migration script to load existing rules from the old system into the new database.
"""
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal, init_db
from app.models.models import Rule, Condition, Question


def auto_detect_visa_type(rule_data: dict) -> str:
    """Auto-detect visa type from rule conclusion"""
    conclusion = rule_data.get("conclusion", "")

    if "Eビザ" in conclusion or "E-" in conclusion:
        return "E"
    elif "Lビザ" in conclusion or "Blanket L" in conclusion:
        return "L"
    elif "Bビザ" in conclusion or "B-1" in conclusion or "B-2" in conclusion:
        return "B"
    elif "H-1B" in conclusion or "H1B" in conclusion:
        return "H-1B"
    elif "J-1" in conclusion or "J1" in conclusion:
        return "J-1"

    return None


def load_rules_from_json(json_file: str):
    """Load rules from JSON file into database"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()

    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Condition).delete()
        db.query(Rule).delete()
        db.query(Question).delete()
        db.commit()

        # Track all fact names for question creation
        fact_names = set()

        print(f"Loading {len(data['rules'])} rules...")

        for rule_data in data["rules"]:
            # Auto-detect visa type
            visa_type = auto_detect_visa_type(rule_data)

            # Create rule
            rule = Rule(
                rule_id=rule_data["id"],
                visa_type=visa_type,
                conclusion=rule_data["conclusion"],
                conclusion_value=rule_data.get("conclusion_value", True),
                operator=rule_data.get("operator", "AND"),
                priority=rule_data.get("priority", 0),
            )
            db.add(rule)
            db.flush()  # Get rule.id

            # Create conditions
            for cond_data in rule_data["conditions"]:
                fact_name = cond_data["fact_name"]
                fact_names.add(fact_name)

                condition = Condition(
                    rule_id=rule.id,
                    fact_name=fact_name,
                    expected_value=cond_data.get("required_value", True),
                )
                db.add(condition)

        print(f"Creating {len(fact_names)} questions...")

        # Create questions for all fact names
        for fact_name in fact_names:
            # Try to auto-detect visa type for the question
            visa_type = None
            if "Eビザ" in fact_name or "E-" in fact_name:
                visa_type = "E"
            elif "Lビザ" in fact_name or "Blanket L" in fact_name:
                visa_type = "L"
            elif "Bビザ" in fact_name or "B-1" in fact_name or "B-2" in fact_name:
                visa_type = "B"
            elif "H-1B" in fact_name or "H1B" in fact_name:
                visa_type = "H-1B"
            elif "J-1" in fact_name or "J1" in fact_name:
                visa_type = "J-1"

            question = Question(
                fact_name=fact_name,
                question_text=fact_name,  # Use fact_name as question text initially
                visa_type=visa_type,
                priority=0,
            )
            db.add(question)

        db.commit()
        print("Migration completed successfully!")

        # Print summary
        rule_count = db.query(Rule).count()
        condition_count = db.query(Condition).count()
        question_count = db.query(Question).count()

        print(f"\nSummary:")
        print(f"  Rules: {rule_count}")
        print(f"  Conditions: {condition_count}")
        print(f"  Questions: {question_count}")

        # Print rules by visa type
        print(f"\nRules by visa type:")
        for visa_type in ["E", "L", "B", "H-1B", "J-1"]:
            count = db.query(Rule).filter(Rule.visa_type == visa_type).count()
            print(f"  {visa_type}: {count}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_db()

    # Path to old rules.json
    old_rules_path = Path(__file__).parent.parent / "visa-expert-system" / "backend" / "app" / "data" / "rules.json"

    if not old_rules_path.exists():
        print(f"Error: Rules file not found at {old_rules_path}")
        sys.exit(1)

    print(f"Loading rules from: {old_rules_path}")
    load_rules_from_json(str(old_rules_path))
