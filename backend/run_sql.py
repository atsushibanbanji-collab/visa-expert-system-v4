"""SQLファイルを実行するシンプルなスクリプト"""
import sqlite3
import sys

def run_sql_file(db_path, sql_file):
    """SQLファイルを実行"""
    try:
        # SQLファイルを読み込む
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # データベースに接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # SQLを実行
        cursor.executescript(sql_script)
        conn.commit()

        print("OK: SQL executed successfully!")

        # 結果を表示
        cursor.execute("""
            SELECT COUNT(*) FROM questions WHERE visa_type IN ('E', 'L', 'B')
        """)
        count = cursor.fetchone()[0]
        print(f"Total questions in database: {count}")

        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    db_path = "visa_expert.db"
    sql_file = "add_questions.sql"
    run_sql_file(db_path, sql_file)
