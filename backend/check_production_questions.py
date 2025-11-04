"""本番環境のデータベースをチェック"""
import requests
import json

BASE_URL = "https://visa-expert-backend-h2oa.onrender.com/api"

def check_questions():
    """質問リストを取得して優先度を確認"""

    print("=" * 80)
    print("本番環境の質問リストをチェック")
    print("=" * 80)

    # すべての質問を取得
    response = requests.get(f"{BASE_URL}/admin/questions")

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return

    questions = response.json()

    # E-visaの質問のみをフィルター
    e_questions = [q for q in questions if q.get('visa_type') == 'E' or q.get('visa_type') is None]

    print(f"\nTotal E-visa questions: {len(e_questions)}")

    # 優先度でソート
    e_questions.sort(key=lambda x: x.get('priority', 0), reverse=True)

    print("\n" + "=" * 80)
    print("Priority 80以上の質問（導出可能な質問）")
    print("=" * 80)

    high_priority = [q for q in e_questions if q.get('priority', 0) >= 80]

    if not high_priority:
        print("ERROR: Priority 80以上の質問が見つかりません！")
        print("マイグレーションが実行されていない可能性があります。")
    else:
        for q in high_priority:
            print(f"Priority {q['priority']:3d}: {q['question_text']}")
            print(f"             Fact: {q['fact_name']}")
            print()

    print("\n" + "=" * 80)
    print("全てのE-visa質問（Priority順）")
    print("=" * 80)

    for q in e_questions[:20]:  # 最初の20件のみ
        print(f"P{q.get('priority', 0):3d}: {q['question_text'][:60]}")

if __name__ == "__main__":
    try:
        check_questions()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
