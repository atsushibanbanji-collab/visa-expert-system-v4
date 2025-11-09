"""
マイグレーション: is_final_conclusionフィールドを追加

1. rulesテーブルにis_final_conclusionカラムを追加
2. 既存データで「申請ができます」「申請が可能です」を含むルールにフラグをセット
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import SessionLocal, engine
from sqlalchemy import text


def migrate():
    """マイグレーションを実行"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("マイグレーション: is_final_conclusionフィールド追加")
        print("=" * 60)

        # Step 1: カラムを追加
        print("\n[1] rulesテーブルにis_final_conclusionカラムを追加...")
        try:
            db.execute(text(
                "ALTER TABLE rules ADD COLUMN is_final_conclusion BOOLEAN DEFAULT 0"
            ))
            db.commit()
            print("   ✓ カラム追加完了")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("   - カラムは既に存在します（スキップ）")
                db.rollback()
            else:
                raise

        # Step 2: 既存データにフラグをセット
        print("\n[2] 最終結論ルールにフラグをセット...")

        # 「申請ができます」「申請が可能です」を含むルールを検索
        result = db.execute(text(
            """
            SELECT id, rule_id, conclusion
            FROM rules
            WHERE conclusion LIKE '%申請ができます%'
               OR conclusion LIKE '%申請が可能です%'
            """
        ))

        final_rules = result.fetchall()
        print(f"   検出された最終結論ルール: {len(final_rules)}件")

        # フラグを更新
        for rule in final_rules:
            db.execute(text(
                """
                UPDATE rules
                SET is_final_conclusion = 1
                WHERE id = :id
                """
            ), {"id": rule[0]})
            print(f"   ✓ {rule[1]}: {rule[2]}")

        db.commit()

        # Step 3: 結果確認
        print("\n[3] 結果確認...")
        result = db.execute(text(
            "SELECT COUNT(*) FROM rules WHERE is_final_conclusion = 1"
        ))
        count = result.fetchone()[0]
        print(f"   最終結論ルール: {count}件")

        result = db.execute(text(
            "SELECT COUNT(*) FROM rules WHERE is_final_conclusion = 0"
        ))
        count = result.fetchone()[0]
        print(f"   中間ルール: {count}件")

        print("\n" + "=" * 60)
        print("マイグレーション完了！")
        print("=" * 60)

    except Exception as e:
        print(f"\nエラー: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
