# ビザエキスパートシステム v4 - 引継ぎドキュメント

## プロジェクト概要

**プロジェクト名**: ビザ選定エキスパートシステム v4
**目的**: オブジェクト指向エキスパートシステムによるビザ診断
**推論方式**: バックワードチェイニング（ゴール指向推論）
**デプロイ環境**: Render (https://render.com)

## ディレクトリ構造

```
C:\Users\GPC999\Documents\works\visa-expert-system-v4\
├── backend/                    # FastAPI バックエンド
│   ├── app/
│   │   ├── api/
│   │   │   └── consultation.py    # 診断API（重要）
│   │   ├── services/
│   │   │   └── inference_engine.py # 推論エンジン（最重要）
│   │   ├── models/
│   │   │   ├── models.py          # SQLAlchemyモデル
│   │   │   ├── schemas.py         # Pydanticスキーマ
│   │   │   └── database.py        # DB設定
│   │   └── main.py                # FastAPIエントリーポイント
│   ├── migrate_rules.py           # ルール移行スクリプト
│   ├── migrate_add_derivable_questions.py  # 導出可能な質問追加スクリプト
│   ├── add_questions.sql          # ローカル開発用SQL
│   ├── run_sql.py                 # SQL実行ユーティリティ
│   └── requirements.txt
├── frontend/                   # React + Vite フロントエンド
│   ├── src/
│   │   ├── pages/
│   │   │   └── ConsultationPage.jsx  # メインページ
│   │   └── components/
│   │       └── consultation/
│   │           ├── DiagnosisPanel.jsx      # 診断パネル
│   │           └── VisualizationPanel.jsx  # 可視化パネル
│   ├── index.html             # ビルドトリガー用コメント含む
│   └── package.json
└── render.yaml                # Renderデプロイ設定（重要）
```

## 技術スタック

### バックエンド
- **フレームワーク**: FastAPI (Python)
- **Python バージョン**: 3.11 (render.yaml で指定)
- **データベース**: SQLite (ローカル), PostgreSQL想定の設計
- **ORM**: SQLAlchemy (Eager loading必須: `joinedload`)
- **推論方式**: Backward Chaining (Goal-Directed Reasoning)

### フロントエンド
- **フレームワーク**: React + Vite
- **言語**: JavaScript (JSX)
- **スタイリング**: Tailwind CSS
- **ビルドツール**: Vite

### デプロイ環境
- **プラットフォーム**: Render
- **バックエンドURL**: https://visa-expert-backend-h2oa.onrender.com
- **フロントエンドURL**: https://visa-expert-frontend-h2oa.onrender.com
- **デプロイ方式**: GitHubプッシュで自動デプロイ

## 現在の実装状況（2025-11-04 最終更新）

### ✅ 完了した機能

#### 1. バックワードチェイニング推論エンジン
- **ファイル**: `backend/app/services/inference_engine.py`
- **主要メソッド**:
  - `get_next_question()`: 次に質問すべき事実を決定
  - `forward_chain()`: 前向き推論で事実を導出
  - `_find_question_for_goal()`: ゴールから逆算して質問を探索
  - `_can_fire_rule()`: ルールの発火可能性を判定

#### 2. 「わからない」回答の高度な処理（最新実装）
- **実装日**: 2025-11-03〜04
- **機能**:
  - **代替パス評価**: 「わからない」条件を含まないルールを優先
  - **クリティカル条件検出**: 代替パスがない重要情報を特定
  - **情報不足時の診断終了**: 適切なメッセージとともに終了
  - **未評価ルールの可視化**: 黄色の破線ボーダーで表示

- **関連メソッド** (`inference_engine.py`):
  - `_has_unknown_conditions(rule)`: ルールが不明条件を含むかチェック
  - `get_missing_critical_info()`: 不足している重要情報を取得
  - `_can_derive_from_alternative(fact_name)`: 代替パスで導出可能かチェック
  - `_find_question_for_goal()`: 代替パス優先のロジック実装済み

- **フロントエンド対応**:
  - `ConsultationPage.jsx`: `missingCriticalInfo`ステート追加
  - `DiagnosisPanel.jsx`: 赤いボックスで不足情報を表示
  - `VisualizationPanel.jsx`: 不明条件を黄色破線で表示

#### 3. 導出可能な質問機能（最新実装）
- **実装日**: 2025-11-04
- **機能**:
  - **高優先度質問の追加**: 導出可能な事実（ルール2,5,15,23の結論）を質問として追加
  - **質問優先度判定**: Priority 80以上の質問は直接聞く
  - **詳細質問への展開**: 「わからない」選択時に詳細質問に進む
  - **診断効率の向上**: 知識がある人は高レベル質問で効率的に診断

- **追加された質問** (10個):
  - 会社がEビザの条件を満たしますか？ (Priority: 95)
  - 申請者がEビザの条件を満たしますか？ (Priority: 85)
  - 会社がEビザの投資（E-2）の条件を満たしますか？ (Priority: 90)
  - 会社がEビザの貿易（E-1）の条件を満たしますか？ (Priority: 90)
  - 申請者がEビザのマネージャー以上の条件を満たしますか？ (Priority: 80)
  - 申請者がEビザのスタッフの条件を満たしますか？ (Priority: 80)
  - Blanket Lビザのマネージャーまたはスタッフの条件を満たしますか？ (Priority: 85)
  - Bビザの申請ができますか？ (Priority: 95)
  - Bビザの申請条件を満たしますか？（ESTAの認証が通る場合） (Priority: 90)
  - Bビザの申請条件を満たしますか？（ESTAの認証が通らない場合） (Priority: 90)

- **関連メソッド** (`inference_engine.py`):
  - `_get_question_priority(fact_name)`: 質問の優先度を取得
  - `_find_question_for_rule()`: 優先度に基づいて質問を決定

- **マイグレーションスクリプト**:
  - `migrate_add_derivable_questions.py`: 本番環境への質問追加スクリプト
  - `add_questions.sql`: ローカル開発用SQLスクリプト

#### 4. ルール可視化機能
- **実装場所**: `VisualizationPanel.jsx`
- **表示内容**:
  - ルールの条件と結論
  - 条件の状態（satisfied, not_satisfied, uncertain, unknown）
  - 発火済み・推論中・未評価の区別
  - 現在の質問に関連するルールへの自動スクロール

#### 5. データベース＆ルール
- **ルール数**: 30個（E/L/Bビザ用）
- **条件数**: 75個
- **質問数**: 73個（基本質問63個 + 導出可能質問10個）
- **移行スクリプト**: `migrate_rules.py`, `migrate_add_derivable_questions.py`

### 🚧 最新の変更（コミット履歴）

#### コミット a997196 (最新)
```
ビルドコマンドに質問マイグレーションを追加
- render.yamlのbuildCommandに導出可能な質問のマイグレーションを追加
- デプロイ時に自動的に新しい質問がデータベースに追加される
```
**変更ファイル**:
- `render.yaml`: buildCommandに`python migrate_add_derivable_questions.py`を追加

#### コミット 8ea9385
```
マイグレーションスクリプトを追加: 導出可能な質問
- 本番環境用のマイグレーションスクリプトを作成
- 10個の高優先度質問を追加
```
**変更ファイル**:
- `backend/migrate_add_derivable_questions.py`: 新規作成

#### コミット 8a35859
```
導出可能な質問の追加と推論エンジンの改善
- 導出可能な事実（rule 2,5,15,23の結論）を高優先度質問として追加
- 「わからない」選択時に詳細質問に進む機能を実装
- 質問優先度判定ロジック追加
```
**変更ファイル**:
- `backend/app/services/inference_engine.py`: `_get_question_priority()`メソッド追加
- `backend/add_questions.sql`: 10個の質問をSQLで定義
- `backend/run_sql.py`: SQL実行ユーティリティ

#### コミット f41eb9f
```
Fix: start_consultation APIレスポンスに不足フィールドを追加
- insufficient_info と missing_critical_info フィールドを追加
- フロントエンドのビルドトリガーを更新
```
**変更ファイル**:
- `backend/app/api/consultation.py`: `start_consultation()`にフィールド追加
- `frontend/index.html`: ビルドトリガー更新 (2025-11-04 00:16)

#### コミット dcbc445
```
Frontend: 「わからない」回答の完全な統合
- ConsultationPage.jsxにmissingCriticalInfo状態を追加
- APIレスポンスからmissing_critical_infoを抽出
- DiagnosisPanelにmissingCriticalInfoプロップを渡す
```

#### コミット 10efa3d
```
Feature: 「わからない」回答の高度な処理を実装
- 代替パスの評価ロジック
- クリティカル条件の判定
- 不足情報リストの生成
- VisualizationPanelのuncertain条件表示
```

## 重要なファイルと役割

### 1. backend/app/services/inference_engine.py
**役割**: バックワードチェイニング推論エンジンの中核

**重要な状態変数**:
```python
self.facts: Dict[str, bool]  # 確定した事実
self.derived_facts: Set[str]  # 導出された事実
self.unknown_facts: Set[str]  # 「わからない」と回答された事実
self.fired_rules: List[str]  # 発火済みルールID
self.goal: str  # 最終ゴール（例: "Eビザでの申請ができます"）
```

**推論フロー**:
1. `get_next_question()` → ゴールから逆算して質問を探索
2. ユーザー回答 → `add_fact()` or `add_unknown_fact()`
3. `forward_chain()` → 新しい事実を導出
4. ループ

**注意点**:
- SQLAlchemy DetachedInstanceErrorを避けるため、`joinedload(Rule.conditions)`を使用
- 可視化エンドポイントでは毎回DBセッションを更新＆キャッシュクリア必須

### 2. backend/app/api/consultation.py
**役割**: 診断APIエンドポイント

**グローバル状態** (シングルユーザー用):
```python
_current_engine = None  # InferenceEngineインスタンス
_question_history = []  # 質問履歴
_visa_type = None  # 選択されたビザタイプ
_current_question_fact = None  # 現在の質問のfact_name
```

**主要エンドポイント**:
- `POST /api/consultation/start`: 診断開始
- `POST /api/consultation/answer`: 質問に回答
- `POST /api/consultation/back`: 前の質問に戻る
- `GET /api/consultation/visualization`: 推論過程の可視化データ取得

**重要**: `/visualization`エンドポイントでは以下を実行:
```python
_current_engine.db = db
_current_engine.all_rules = None
_current_engine.rules_by_conclusion.clear()
```

### 3. backend/app/models/schemas.py
**役割**: APIレスポンススキーマ定義

**ConsultationResponse** (最重要):
```python
class ConsultationResponse(BaseModel):
    next_question: Optional[str] = None
    conclusions: List[str] = []
    is_finished: bool = False
    unknown_facts: List[str] = []
    insufficient_info: bool = False
    missing_critical_info: List[str] = []  # 必須フィールド
```

### 4. frontend/src/pages/ConsultationPage.jsx
**役割**: メインページ、状態管理

**主要ステート**:
```javascript
const [missingCriticalInfo, setMissingCriticalInfo] = useState([])
const [insufficientInfo, setInsufficientInfo] = useState(false)
const [unknownFacts, setUnknownFacts] = useState([])
const [currentQuestion, setCurrentQuestion] = useState(null)
const [conclusions, setConclusions] = useState([])
const [visualizationData, setVisualizationData] = useState(null)
```

**APIコール**:
- `startConsultation()`: `/api/consultation/start`
- `handleAnswer()`: `/api/consultation/answer`
- `fetchVisualization()`: `/api/consultation/visualization`

### 5. frontend/src/components/consultation/DiagnosisPanel.jsx
**役割**: 診断結果と質問の表示

**表示内容**:
- 現在の質問と回答ボタン（はい / いいえ / 分からない）
- 診断結果（成功時）
- 不足情報メッセージ（情報不足時）
- **赤いボックス**: `missingCriticalInfo`の表示

### 6. frontend/src/components/consultation/VisualizationPanel.jsx
**役割**: 推論過程の可視化

**条件の色分け**:
```javascript
'satisfied' → 緑（条件満たす）
'not_satisfied' → 赤（条件満たさない）
'uncertain' → 黄色破線（わからない）
'unknown' → 灰色（未評価）
```

**ルールの状態**:
```javascript
'fired' → 青（発火済み）
'evaluating' → オレンジ（推論中）
'unfireable' → 赤（発火不可能）
'pending' → 灰色（未評価）
```

### 7. render.yaml
**役割**: Renderデプロイ設定

**重要な設定**:
```yaml
services:
  - type: web
    name: visa-expert-backend-h2oa
    env: python
    region: oregon
    runtime: python-3.11  # 必須！
    buildCommand: cd backend && pip install -r requirements.txt && python migrate_rules.py && python migrate_add_derivable_questions.py
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

  - type: static
    name: visa-expert-frontend-h2oa
    buildCommand: npm install && npm run build
    staticPublishPath: ./dist
    envVars:
      - key: VITE_API_URL
        value: https://visa-expert-backend-h2oa.onrender.com/api
```

**注意**: フロントエンドのAPI URLには`-h2oa`サフィックスが必須！

## ローカル開発環境

### バックエンド起動
```bash
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```
→ http://127.0.0.1:8000

### フロントエンド起動
```bash
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\frontend
npm install
npm run dev
```
→ http://localhost:5173

### データベース初期化
```bash
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\backend
py migrate_rules.py
```

## デプロイ手順

1. **変更をコミット**:
```bash
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4
git add .
git commit -m "変更内容"
git push
```

2. **Renderが自動デプロイ**:
   - GitHubプッシュを検知して自動的にデプロイ開始
   - 通常5-10分で完了

3. **デプロイ確認**:
```bash
curl -s https://visa-expert-backend-h2oa.onrender.com/
curl -s https://visa-expert-frontend-h2oa.onrender.com/
```

4. **フロントエンドの強制リビルド** (必要な場合):
   - `frontend/index.html`のコメントを更新:
   ```html
   <!-- Rebuild trigger: 2025-11-04 XX:XX -->
   ```

## 既知の問題と解決策

### 1. SQLAlchemy DetachedInstanceError
**エラー**: `Parent instance <Rule> is not bound to a Session`

**原因**: キャッシュされたRuleオブジェクトで古いDBセッションから`rule.conditions`にアクセス

**解決策**:
```python
# Eager loading
self.all_rules = (
    self.db.query(Rule)
    .options(joinedload(Rule.conditions))  # 必須！
    .filter(Rule.visa_type == self.visa_type)
    .order_by(Rule.priority.desc())
    .all()
)

# 可視化エンドポイントでキャッシュクリア
_current_engine.db = db
_current_engine.all_rules = None
_current_engine.rules_by_conclusion.clear()
```

### 2. Python型ヒントの互換性エラー
**エラー**: `tuple[bool, bool]` がPython 3.8で動かない

**解決策**:
```python
from typing import Tuple

# NG: tuple[bool, bool]
# OK: Tuple[bool, bool]
```

また、`render.yaml`で明示的にPythonバージョンを指定:
```yaml
runtime: python-3.11
```

### 3. CORS / API URL の404エラー
**原因**: フロントエンドのAPI URLに`-h2oa`サフィックスが欠けている

**確認**:
```yaml
# render.yaml
envVars:
  - key: VITE_API_URL
    value: https://visa-expert-backend-h2oa.onrender.com/api  # -h2oa必須
```

### 4. デプロイタイムアウト
**原因**: ビルドに時間がかかりすぎる

**対処法**:
- Renderダッシュボードでログを確認
- エラーがなければ、数分待ってから再度アクセス
- 必要に応じてフロントエンドのビルドトリガーを更新して再デプロイ

## テストシナリオ

### 導出可能な質問機能のテスト（最新）

1. **ブラウザでアクセス**:
   - ローカル: http://localhost:5173
   - 本番: https://visa-expert-frontend-h2oa.onrender.com

2. **Eビザを選択**して診断開始

3. **最初の質問**: "申請者と会社の国籍が同じです"
   - 「はい」をクリック

4. **2番目の質問（高レベル質問）**: "会社がEビザの条件を満たしますか？"
   - **知識がある人**: 「はい」をクリック → 次の高レベル質問へ
   - **知識がない人**: 「分からない」をクリック → 詳細質問へ

5. **「分からない」を選択した場合の確認項目**:
   - ✅ 次の質問が詳細質問（例: "会社がEビザの投資（E-2）の条件を満たしますか？"）
   - ✅ 可視化パネルで「会社がEビザの条件を満たします」が黄色破線で表示
   - ✅ より具体的な会社要件の質問が提示される

6. **「はい」を選択した場合の確認項目**:
   - ✅ 次の質問が別の高レベル質問（例: "申請者がEビザの条件を満たしますか？"）
   - ✅ 診断が効率的に進む（詳細質問をスキップ）

### 「わからない」回答機能のテスト

1. **ブラウザでアクセス**:
   - ローカル: http://localhost:5173
   - 本番: https://visa-expert-frontend-h2oa.onrender.com

2. **Eビザを選択**して診断開始

3. **最初の質問**: "申請者と会社の国籍が同じです"
   - 「分からない」をクリック

4. **確認項目**:
   - ✅ 可視化パネルで該当条件が**黄色の破線ボーダー**で表示
   - ✅ 代替パスがあれば別の質問が提示される
   - ✅ 代替パスがなければ診断が終了

5. **診断終了時の確認**:
   - ✅ 「診断できませんでした」メッセージ
   - ✅ 黄色のボックス: 「分からない」と回答した条件のリスト
   - ✅ **赤いボックス**: 診断を完了するために必要な重要情報のリスト

### APIの直接テスト

```bash
# 診断開始
curl -s -X POST https://visa-expert-backend-h2oa.onrender.com/api/consultation/start \
  -H "Content-Type: application/json" \
  -d '{"visa_type":"E"}'

# レスポンスに以下が含まれることを確認
# - next_question
# - insufficient_info: false
# - missing_critical_info: []

# 可視化データ取得
curl -s https://visa-expert-backend-h2oa.onrender.com/api/consultation/visualization

# レスポンスに以下が含まれることを確認
# - rules (配列)
# - fired_rules (配列)
# - current_question_fact (文字列)
```

## 次回セッション開始時の確認事項

1. **このファイルを読み込む**:
```bash
Read: C:\Users\GPC999\Documents\works\visa-expert-system-v4\HANDOFF.md
```

2. **現在のデプロイ状況を確認**:
```bash
curl -s https://visa-expert-backend-h2oa.onrender.com/
curl -s https://visa-expert-frontend-h2oa.onrender.com/
```

3. **ローカル開発環境の状態確認** (必要な場合):
```bash
# バックエンド
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\backend
py -m uvicorn app.main:app --reload

# フロントエンド
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\frontend
npm run dev
```

4. **最新のGit状態確認**:
```bash
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4
git status
git log --oneline -5
```

## 追加リソース

### 参考ドキュメント
- **システムイメージ**: `C:\Users\GPC999\Documents\works\システムイメージ.txt`
- **ビザ選定知識**: `C:\Users\GPC999\Documents\works\ビザ選定知識.txt`

### 関連URL
- **GitHubリポジトリ**: https://github.com/atsushibanbanji-collab/visa-expert-system-v4
- **Render ダッシュボード**: https://dashboard.render.com/
- **バックエンドAPI**: https://visa-expert-backend-h2oa.onrender.com/docs (FastAPI Swagger)

## まとめ

**現在の状態**:
- ✅ バックワードチェイニング推論エンジン完成
- ✅ 「わからない」回答の高度な処理実装完了
- ✅ 導出可能な質問機能実装完了（NEW）
- ✅ 質問優先度判定ロジック実装完了（NEW）
- ✅ フロントエンド統合完了
- ✅ 最新コード（a997196）をGitHubにプッシュ済み
- ✅ Renderでのデプロイ設定完了（自動マイグレーション含む）

**次のアクション**:
1. Renderでのデプロイ完了を待つ（5-10分）
2. 本番環境で導出可能な質問機能をテスト
3. 知識がある人・ない人の両方のフローをテスト
4. 問題があれば修正、なければ完了

**重要な注意事項**:
- シングルユーザー設計（グローバル状態使用）
- SQLAlchemy Eager loadingは必須
- フロントエンドAPI URLには必ず`-h2oa`サフィックスを含める
- Python 3.11を使用（型ヒント互換性のため）

---

**作成日**: 2025-11-04 00:20
**最終更新**: 2025-11-04 (コミット a997196)
**作成者**: Claude Code
