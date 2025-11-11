"""
Bビザのルール優先度を修正して、E・Lビザと同様のフローにする
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal
from app.models.models import Rule


def fix_b_visa_priority():
    """Bビザの通常ケース（Rule 23）を最優先にする"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("Bビザルール優先度修正")
        print("=" * 60)

        # Rule 23 (通常のBビザ) を最優先にする
        rule_23 = db.query(Rule).filter(Rule.rule_id == "rule_23").first()

        if rule_23:
            old_priority = rule_23.priority
            rule_23.priority = 101  # 他のBビザルールより優先

            print(f"\n✓ Rule 23: {rule_23.conclusion}")
            print(f"  priority: {old_priority} → 101")
            print(f"  理由: 通常のBビザ診断を優先（E・Lビザと同じパターン）")

            db.commit()

            print("\n" + "=" * 60)
            print("修正完了")
            print("=" * 60)

            # 確認
            print("\nBビザルール一覧（優先度順）:")
            b_rules = (
                db.query(Rule)
                .filter(Rule.visa_type == "B")
                .filter(Rule.is_final_conclusion == True)
                .order_by(Rule.priority.desc(), Rule.rule_id)
                .all()
            )

            for rule in b_rules:
                print(f"  {rule.rule_id} (priority {rule.priority}): {rule.conclusion}")

            return True
        else:
            print("\n✗ Rule 23 not found")
            return False

    except Exception as e:
        print(f"\nエラー: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting migration: Fix B visa rule priority...")
    success = fix_b_visa_priority()
    sys.exit(0 if success else 1)
