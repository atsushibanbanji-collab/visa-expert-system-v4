#!/bin/bash
# クイック保存スクリプト - 作業中の変更を即座にローカルコミット
# 使い方: bash quick-save.sh "変更内容の説明"

cd "$(dirname "$0")"

# 変更があるかチェック
if [[ -z $(git status -s) ]]; then
    echo "[OK] 変更なし - コミットの必要はありません"
    exit 0
fi

# コミットメッセージを取得（引数があればそれを使用、なければタイムスタンプ）
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
    COMMIT_MSG="WIP: 作業保存 $TIMESTAMP"
fi

echo ""
echo "=== クイック保存 ==="
echo "時刻: $(date)"
echo ""

# 変更されたファイルを表示
echo "[変更されたファイル:]"
git status --short
echo ""

# 全てをステージング
git add -A

# コミット
git commit -m "$COMMIT_MSG

🤖 Quick save by Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

if [ $? -ne 0 ]; then
    echo "[ERROR] コミットに失敗しました"
    exit 1
fi

echo ""
echo "[OK] 保存完了！"
echo ""
echo "最新のコミット:"
git log -1 --oneline
echo ""
echo "--- 復元方法 ---"
HASH=$(git log -1 --format="%h")
echo "このコミットに戻る: git checkout $HASH"
echo "直前に戻る: git reset --soft HEAD~1"
echo ""

exit 0
