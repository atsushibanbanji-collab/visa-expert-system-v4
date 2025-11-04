"""本番環境でマイグレーションを実行"""
import requests
from getpass import getpass

BASE_URL = "https://visa-expert-backend-h2oa.onrender.com/api"

def run_migration():
    """管理者エンドポイントを使ってマイグレーションを実行"""

    print("=" * 80)
    print("本番環境でマイグレーションを実行")
    print("=" * 80)

    # Get admin credentials
    print("\n管理者認証が必要です:")
    username = input("Username (default: admin): ") or "admin"
    password = getpass("Password: ")

    # Run migration
    print("\nマイグレーションを実行中...")
    response = requests.post(
        f"{BASE_URL}/admin/migrate/derivable-questions",
        auth=(username, password)
    )

    if response.status_code == 401:
        print("ERROR: 認証に失敗しました。ユーザー名とパスワードを確認してください。")
        return False

    if response.status_code != 200:
        print(f"ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        return False

    result = response.json()
    print("\n" + "=" * 80)
    print("マイグレーション結果")
    print("=" * 80)
    print(f"Success: {result.get('success')}")
    print(f"Added: {result.get('added')}")
    print(f"Updated: {result.get('updated')}")
    print(f"Skipped: {result.get('skipped')}")
    print(f"\nMessage: {result.get('message')}")

    if result.get('added', 0) > 0 or result.get('updated', 0) > 0:
        print("\nマイグレーションが成功しました！")
        print("診断フローをテストしてください。")
        return True
    else:
        print("\n警告: 質問が追加されませんでした。")
        print("質問がすでに存在している可能性があります。")
        return False

if __name__ == "__main__":
    try:
        success = run_migration()

        if success:
            print("\n" + "=" * 80)
            print("次のステップ:")
            print("=" * 80)
            print("1. https://visa-expert-frontend-h2oa.onrender.com/ にアクセス")
            print("2. Eビザを選択")
            print("3. 全ての質問に「はい」と答える")
            print("4. 期待される質問順序:")
            print("   - 申請者と会社の国籍が同じです")
            print("   - 会社がEビザの条件を満たしますか？")
            print("   - 申請者がEビザの条件を満たしますか？")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
