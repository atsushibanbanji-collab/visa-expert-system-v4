# 変更を確実に保存するガイド

このガイドは、作業中の変更を見失わないための簡単な手順をまとめています。

## 🚀 超簡単！3つの保存方法

### 方法1: クイック保存（推奨）⭐

**今すぐ保存したい時**
```bash
# Windowsの場合
quick-save.bat

# Git Bashの場合
bash quick-save.sh
```

**説明付きで保存したい時**
```bash
quick-save.bat "わからない機能の改善中"
```

これだけ！変更が全てローカルにコミットされます。

---

### 方法2: 手動コミット

```bash
# 変更を確認
git status

# 全ての変更を保存
git add -A
git commit -m "変更内容の説明"
```

---

### 方法3: 自動バックアップ（定期実行用）

```bash
# 日付ごとのバックアップブランチを自動作成
auto-backup.bat
```

---

## 📅 推奨ワークフロー

### 作業開始時
```bash
# 現在地を確認
git branch
# -> * main

# 状態を確認
git status
```

### 作業中（こまめに保存）
```bash
# 30分〜1時間ごと、または機能が動いたら
quick-save.bat "○○を実装"
```

### 作業終了時
```bash
# 最終保存
quick-save.bat "今日の作業完了"

# 状態確認
git log --oneline -5
```

---

## 🔍 保存したコミットの確認

### 最近のコミットを見る
```bash
git log --oneline -10
```

### 特定のファイルの変更履歴
```bash
git log --oneline -- backend/app/services/inference_engine.py
```

### コミットの詳細を見る
```bash
git show <コミットハッシュ>
```

---

## 🛡️ 復元方法

### 直前のコミットに戻る
```bash
# 変更を保持したまま戻る
git reset --soft HEAD~1

# 変更も全て破棄して戻る（注意！）
git reset --hard HEAD~1
```

### 特定のコミットに戻る
```bash
git checkout <コミットハッシュ>
```

### 特定のファイルだけ復元
```bash
git checkout <コミットハッシュ> -- path/to/file.py
```

---

## ⚠️ よくある質問

### Q: コミットし忘れた！
**A**: `git reflog` で履歴を確認できます
```bash
git reflog
# コミット前の状態が見つかったら
git checkout <ハッシュ>
```

### Q: 間違えてコミットした
**A**: `git reset` で取り消せます
```bash
# コミットだけ取り消し（変更は保持）
git reset --soft HEAD~1

# コミットと変更を全て取り消し
git reset --hard HEAD~1
```

### Q: 複数の場所で作業していて混乱
**A**: 常に同じディレクトリで作業しましょう
```bash
# 現在地を確認
pwd
# -> C:\Users\GPC999\visa-expert-system-v4 ✓ これを使う
```

---

## 🎯 ベストプラクティス

### ✅ DO（やること）
- [ ] 30分〜1時間ごとに `quick-save.bat`
- [ ] 機能が動いたら即座に保存
- [ ] わかりやすいコミットメッセージ
- [ ] 1日の終わりに必ず保存

### ❌ DON'T（やらないこと）
- [ ] 「後でまとめてコミット」は禁物
- [ ] リモートへの不用意なpush
- [ ] 複数ディレクトリでの並行作業
- [ ] コミットせずにブランチ切り替え

---

## 📞 緊急時

変更が見つからない場合：

```bash
# 1. reflogで全履歴を確認
git reflog --all

# 2. 全ブランチで検索
git log --all --oneline --grep="キーワード"

# 3. 特定ファイルの全履歴
git log --all --follow -- path/to/file.py

# 4. それでも見つからなければ
# RECOVERY_REPORT.md を参照
cat RECOVERY_REPORT.md
```

---

## 🏷️ リカバリーポイント

現在のリカバリーポイント:
```
タグ: recovery-point-2025-11-19
説明: uncertain_facts実装を復元した時点
```

このポイントに戻る:
```bash
git checkout recovery-point-2025-11-19
```

---

**最終更新**: 2025-11-19 23:15
**バージョン**: 1.0
