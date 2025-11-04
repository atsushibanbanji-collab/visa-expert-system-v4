"""本番環境のAPIをテストして、導出可能な質問が正しく聞かれるか確認"""
import requests
import json

BASE_URL = "https://visa-expert-backend-h2oa.onrender.com/api"

def test_all_yes_flow():
    """全ての質問に「はい」と答えた場合のテスト"""

    # Start consultation
    print("=" * 80)
    print("本番環境テスト: 全ての質問に「はい」と答える")
    print("=" * 80)

    response = requests.post(
        f"{BASE_URL}/consultation/start",
        json={"visa_type": "E"}
    )
    data = response.json()

    step = 1
    questions = []

    while not data.get("is_finished"):
        question = data.get("next_question")
        if not question:
            break

        print(f"\nStep {step}: {question}")
        questions.append(question)

        # Answer "yes" to all questions
        response = requests.post(
            f"{BASE_URL}/consultation/answer",
            json={"question": question, "answer": True}
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            break

        data = response.json()

        step += 1

        if step > 20:  # Safety limit
            print("\nStopping: Reached 20 questions")
            break

    # Show results
    print("\n" + "=" * 80)
    print("結果")
    print("=" * 80)
    print(f"Total questions: {len(questions)}")
    print(f"Conclusions: {data.get('conclusions', [])}")
    print(f"Is finished: {data.get('is_finished')}")

    # Show question list
    print("\n" + "=" * 80)
    print("質問順序")
    print("=" * 80)
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")

    # Expected flow
    print("\n" + "=" * 80)
    print("期待される質問順序")
    print("=" * 80)
    print("1. 申請者と会社の国籍が同じです")
    print("2. 会社がEビザの条件を満たしますか？ (導出可能な質問)")
    print("3. 申請者がEビザの条件を満たしますか？ (導出可能な質問)")

    # Check if matches expected
    if len(questions) == 3:
        print("\n✓ 質問数が期待通り！")
    else:
        print(f"\n✗ 質問数が期待と異なる (期待: 3, 実際: {len(questions)})")

if __name__ == "__main__":
    try:
        test_all_yes_flow()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
