"""本番環境の診断フローをデバッグ"""
import requests
import json

BASE_URL = "https://visa-expert-backend-h2oa.onrender.com/api"

def debug_flow():
    """診断フローを開始して最初の質問を確認"""

    print("=" * 80)
    print("本番環境の診断フローをデバッグ")
    print("=" * 80)

    # Start consultation
    response = requests.post(
        f"{BASE_URL}/consultation/start",
        json={"visa_type": "E"}
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return

    data = response.json()

    print("\nStep 1の質問:")
    print(f"  Question: {data.get('next_question')}")
    print(f"  Is finished: {data.get('is_finished')}")
    print(f"  Conclusions: {data.get('conclusions')}")

    print("\n期待される質問: 申請者と会社の国籍が同じです")

    if data.get('next_question') == "申請者と会社の国籍が同じです":
        print("OK: 最初の質問は正しい")
    else:
        print("ERROR: 最初の質問が期待と異なります！")
        return

    # Answer "yes" to first question
    print("\n" + "=" * 80)
    print("最初の質問に「はい」と回答")
    print("=" * 80)

    response = requests.post(
        f"{BASE_URL}/consultation/answer",
        json={"question": data.get('next_question'), "answer": True}
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return

    data = response.json()

    print("\nStep 2の質問:")
    print(f"  Question: {data.get('next_question')}")

    print("\n期待される質問: 会社がEビザの条件を満たしますか？")

    if "会社がEビザの条件を満たしますか" in str(data.get('next_question')):
        print("OK: 2番目の質問は正しい（導出可能な質問）")
    else:
        print("ERROR: 2番目の質問が期待と異なります！")
        print(f"実際の質問: {data.get('next_question')}")
        print("\nこれは詳細な質問です。導出可能な質問が優先されていません。")

if __name__ == "__main__":
    try:
        debug_flow()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
