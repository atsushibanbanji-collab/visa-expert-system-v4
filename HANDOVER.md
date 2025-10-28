# Visa Expert System v4 - 引継ぎメモ

> 最終更新: 2025-10-27
>
> このドキュメントを新しいClaude Codeセッションで読み込ませることで、プロジェクトの現状と作業内容を即座に把握できます。

---

## プロジェクト概要

**ビザ選定エキスパートシステム v4**
- オブジェクト指向エキスパートシステム（前向き推論）
- FastAPI（Python）バックエンド + React（Vite）フロントエンド
- ルールベース推論で最適なビザタイプを診断
- **対応ビザタイプ**: E（投資・貿易）、L（企業内転勤）、B（商用・観光）のみ
  - ⚠️ H-1BとJ-1は**追加しない**（ユーザー明示的要望）

---

## デプロイ情報

### 本番環境（Render）
- **フロントエンド**: https://visa-expert-frontend-h2oa.onrender.com/
- **バックエンド**: https://visa-expert-backend-h2oa.onrender.com/
- **APIヘルスチェック**: https://visa-expert-backend-h2oa.onrender.com/api/health

### 環境変数設定
- **バックエンド**: `backend/.env` に設定済み
- **フロントエンド**: Renderダッシュボードで `VITE_API_URL=https://visa-expert-backend-h2oa.onrender.com/api` 設定済み
  - ⚠️ `-h2oa` サフィックスが重要（404エラーの原因となる）

### Gitリポジトリ
- **GitHub**: https://github.com/atsushibanbanji-collab/visa-expert-system-v4.git
- **ブランチ**: main
- **最新コミット**: `4d6d0ea` - "Fix: 発火可能なルールの結論も波及表示に含める"

---

## 最近の実装内容（重要）

### 1. 発火不可能ルールの表示
**問題**: AND条件なのに「いいえ」が含まれても「推論中」になっていた

**解決策**:
- `backend/app/services/inference_engine.py:234-242` に `is_fireable` ロジックを追加
  - AND: 1つでも `not_satisfied` があれば発火不可能
  - OR: 全て既知で1つも満たされていなければ発火不可能
- フロントエンドで「発火不可能」バッジ（赤色、opacity 60%）を表示

### 2. 早期診断終了
**要件**: 最終結論（「Eビザでの申請ができます」など）が不可能になったら診断終了

**実装**:
- `backend/app/services/inference_engine.py:123-132` で最終結論ルールを特定し、発火不可能なら `None` を返す

### 3. 推論の波及表示（カスケーディング）
**要件**: 発火済みルールの結論を条件として使うルールも表示する

**実装**:
- `frontend/src/components/consultation/VisualizationPanel.jsx:48-62` で `potentialConclusions` を構築
  - 発火済みルールの結論
  - **発火可能かつ現在の質問に関連するルールの結論** ← 最重要修正（2025-10-27）
- これにより、Rule 3が現在の質問に関連している時、Rule 2（Rule 3の結論を使う）も表示される

### 4. 現在の質問に関連するルールの表示
**問題**: 質問テキストとfact_nameが一致せず、関連ルールが表示されなかった

**解決策**:
- `backend/app/api/consultation.py:14` にグローバル変数 `_current_question_fact` を追加
- `start`, `answer`, `back` エンドポイントで更新
- `visualization` エンドポイントで `current_question_fact` を返却
- フロントエンドで `currentQuestion` の代わりに `current_question_fact` で比較

---

## ディレクトリ構造

```
C:\Users\GPC999\Documents\works\
├── visa-expert-system-v4/          ← 現在使用中
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── consultation.py    # 診断フロー、current_question_fact管理
│   │   │   ├── services/
│   │   │   │   └── inference_engine.py # 前向き推論、is_fireable計算
│   │   │   └── models/
│   │   │       └── schemas.py          # is_fireable, current_question_fact追加済み
│   │   ├── .env                        # 環境変数
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/consultation/
│   │   │   │   ├── VisualizationPanel.jsx  # potentialConclusions実装
│   │   │   │   ├── DiagnosisPanel.jsx
│   │   │   │   └── VisaTypeSelection.jsx  # E, L, Bのみ
│   │   │   └── pages/
│   │   │       └── ConsultationPage.jsx
│   │   └── .env                        # ローカル: VITE_API_URL=http://localhost:8000/api
│   ├── README.md
│   ├── QUICKSTART.md
│   └── HANDOVER.md                     # このファイル
├── Smalltalk資料.pdf
├── システムイメージ.txt
└── ビザ選定知識.txt
```

---

## 重要な技術的詳細

### 推論エンジンの仕組み

1. **前向き推論（Forward Chaining）**:
   - ユーザーの回答から事実（fact）を蓄積
   - ルールの条件が全て満たされたら結論を導出
   - 導出された結論は新しい事実として扱われる（カスケーディング）

2. **ルールの優先度**:
   - 高い優先度のルールから質問
   - 最終結論ルール（「での申請ができます」を含む）が最優先

3. **発火可能性の判定**:
   - **AND**: 1つでも条件が満たされないと分かったら発火不可能
   - **OR**: 全ての条件が既知で、1つも満たされていなければ発火不可能

### フロントエンドの表示ロジック

**relevantRules フィルタリング（VisualizationPanel.jsx:64-104）**:
- ✅ 発火済みのルール (`is_fired`)
- ✅ 条件の一部が評価済み (`status !== 'unknown'`)
- ✅ 現在の質問に関連 (`fact_name === current_question_fact`)
- ✅ 発火済み or 発火可能なルールの結論を使用（波及）

**ルールの状態バッジ**:
- 🔵 発火済み (`is_fired`)
- 🟡 今の質問に関係 (`relatedToCurrentQuestion`)
- 🟠 推論中 (`hasEvaluatedCondition`)
- 🔴 発火不可能 (`!is_fireable`)
- ⚪ 未評価

---

## デバッグ情報

### 現在残存しているデバッグログ

`frontend/src/components/consultation/VisualizationPanel.jsx`:
- **Line 42-46**: 全体デバッグ情報（`current_question_fact`, ルール数、発火済みルール）
- **Line 86-101**: **Rule 2とRule 3に限定されたデバッグログ** ⚠️
- **Line 107-110**: フィルタリング後のルール一覧

### 推奨クリーンアップ
Line 86-101 は特定ルールに限定されており、問題が解決したため削除推奨。
他のログは開発モードのみ表示するよう条件分岐を追加することも検討。

---

## よく使うコマンド

### ローカル開発

```bash
# バックエンド起動
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\backend
python -m uvicorn app.main:app --reload

# フロントエンド起動
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\frontend
npm run dev
```

### デプロイ

```bash
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4
git add .
git commit -m "メッセージ"
git push origin main
```

Renderは自動デプロイされます（main ブランチへのpush時）。

### デプロイ確認

```bash
# フロントエンド
curl -s https://visa-expert-frontend-h2oa.onrender.com/

# バックエンドヘルスチェック
curl -s https://visa-expert-backend-h2oa.onrender.com/api/health
```

---

## 整合性チェック結果（2025-10-27実施）

| 項目 | 評価 | 備考 |
|------|------|------|
| ロジック整合性 | ✅ 優 | 論理的な矛盾なし |
| データフロー | ✅ 優 | バックエンド-フロントエンド間で正しく連携 |
| エッジケース処理 | ✅ 優 | 全ケースで適切な処理 |
| パフォーマンス | ✅ 良 | 実用上問題なし（O(n×m)、約30ルール） |
| コード品質 | ⚠️ 良 | デバッグログの残存のみ |

**結論**: システムは正常に動作中。大きな不具合は検出されず。

---

## 既知の問題

### なし
現在、システムは正常に動作しています。

---

## 今後の作業候補（オプション）

1. **デバッグログのクリーンアップ**（優先度: 中）
   - Line 86-101 の特定ルールに限定されたログを削除
   - 開発モードのみ表示する条件分岐を追加

2. **パフォーマンス最適化**（優先度: 低）
   - `useMemo` で `potentialConclusions` と `relevantRules` をメモ化
   - ルール数が100以上に増えた場合のみ検討

3. **テストの追加**（優先度: 低）
   - ユニットテスト（推論エンジン）
   - E2Eテスト（診断フロー）

---

## 重要な制約事項

1. ⚠️ **H-1BとJ-1ビザは追加しない**（ユーザー明示的要望）
2. 診断終了条件: 最終結論が不可能になった時点で終了
3. 質問の順序: ルールの優先度順
4. ビザタイプ選択後の診断は1セッション（グローバル変数で管理）

---

## トラブルシューティング

### 404 エラー（API接続失敗）
- Renderの環境変数 `VITE_API_URL` を確認
- 正しいURL: `https://visa-expert-backend-h2oa.onrender.com/api` （`-h2oa` 必須）

### ルールが表示されない
- ブラウザコンソールでデバッグログを確認
- `current_question_fact` が正しく設定されているか確認
- `potentialConclusions` に期待する結論が含まれているか確認

### 推論が終わらない
- 最終結論ルールの優先度が最高になっているか確認
- `_is_rule_potentially_fireable` のロジックを確認

---

## 連絡先・リソース

- **GitHub**: https://github.com/atsushibanbanji-collab/visa-expert-system-v4
- **Render Dashboard**: https://dashboard.render.com/
- **ドキュメント**: README.md, QUICKSTART.md

---

## このメモの使い方

新しいClaude Codeセッションで以下のメッセージを送信してください：

```
C:\Users\GPC999\Documents\works\visa-expert-system-v4\HANDOVER.md を読んで、このプロジェクトの現状を把握してください。
```

これにより、即座に作業を再開できます。
