# ビザ選定エキスパートシステム v4.0

オブジェクト指向設計による前向き推論エンジンを使用したビザ選定診断システム

## 主な機能

### 診断機能
- **3種類のビザ対応**: Eビザ、Lビザ、Bビザ
- **一問一答形式**: 対話型の質問で段階的に診断
- **リアルタイム可視化**: 推論過程を視覚的に確認
- **ナビゲーション機能**: 前の質問に戻る・やり直し機能
- **2画面分割UI**: 診断画面と推論過程可視化を同時表示

### 管理機能（新機能）
- **ルール管理**: ルールの追加・編集・削除
- **質問管理**: 質問文の編集と優先度設定
- **整合性チェック**:
  - 矛盾検出（同じ条件から異なる結論）
  - 循環参照検出
  - 到達不可能ルール検出
- **変更履歴**: すべての変更を記録

## 技術スタック

### バックエンド
- **FastAPI** - 高速なWeb APIフレームワーク
- **SQLAlchemy** - Python ORM
- **PostgreSQL** (本番) / **SQLite** (開発)
- **Pydantic** - データバリデーション

### フロントエンド
- **React 18** - UIライブラリ
- **Vite** - 高速ビルドツール
- **React Router** - ルーティング
- **Tailwind CSS** - CSSフレームワーク

## セットアップ手順

### 前提条件
- Python 3.8以上
- Node.js 16以上
- npm または yarn

### 1. バックエンドのセットアップ

```bash
# backend ディレクトリに移動
cd backend

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt

# データベース初期化とルール移行
python migrate_rules.py
```

### 2. バックエンドの起動

```bash
# backend ディレクトリで実行
uvicorn app.main:app --reload
```

バックエンドが http://localhost:8000 で起動します。

### 3. フロントエンドのセットアップ

```bash
# 新しいターミナルを開き、frontend ディレクトリに移動
cd frontend

# 依存パッケージのインストール
npm install
```

### 4. フロントエンドの起動

```bash
# frontend ディレクトリで実行
npm run dev
```

フロントエンドが http://localhost:5173 で起動します。

### 5. アプリケーションにアクセス

ブラウザで http://localhost:5173 を開きます。

## 管理画面へのアクセス

1. トップページで「管理画面」をクリック
2. 認証情報を入力:
   - **ユーザー名**: admin
   - **パスワード**: admin123

## デプロイ（Render）

このリポジトリはRenderで自動デプロイされます。

### 必要な環境変数
- `DATABASE_URL`: PostgreSQLの接続URL（Renderが自動設定）
- `ADMIN_USERNAME`: 管理画面のユーザー名（デフォルト: admin）
- `ADMIN_PASSWORD`: 管理画面のパスワード（デフォルト: admin123）

## プロジェクト構造

```
visa-expert-system-v4/
├── backend/
│   ├── app/
│   │   ├── api/              # APIエンドポイント
│   │   ├── models/           # データベースモデル
│   │   ├── services/         # ビジネスロジック
│   │   └── data/             # ルール定義（JSON）
│   ├── migrate_rules.py      # データ移行スクリプト
│   ├── requirements.txt      # Python依存関係
│   └── .env                  # 環境変数
├── frontend/
│   ├── src/
│   │   ├── components/       # Reactコンポーネント
│   │   ├── pages/            # ページコンポーネント
│   │   └── App.jsx           # メインアプリ
│   ├── package.json          # npm依存関係
│   └── .env                  # 環境変数
└── README.md
```

## アーキテクチャ

### 推論エンジン
- **前向き推論（Forward Chaining）**: 既知の事実から新しい事実を導出
- **ルールベース**: IF-THENルールで知識を表現
- **自動導出**: 推論可能な事実は質問をスキップ
- **優先度管理**: ルールの優先度に基づいて質問順序を決定

### データベース設計
- **Rules**: ルール本体（ID、結論、優先度、演算子）
- **Conditions**: ルールの条件（事実名、期待値）
- **Questions**: 質問マスタ（事実名、質問文、優先度）
- **RuleHistory**: 変更履歴（アクション、変更内容、タイムスタンプ）
- **ValidationResult**: 整合性チェック結果（検証タイプ、重要度、メッセージ）

## API エンドポイント

### 診断関連
- `POST /api/consultation/start` - 診断セッションを開始
- `POST /api/consultation/answer` - 質問に回答
- `POST /api/consultation/back` - 前の質問に戻る
- `GET /api/consultation/visualization` - 推論過程の可視化データを取得

### 管理関連（Basic認証が必要）
- `GET /api/admin/rules` - すべてのルールを取得
- `POST /api/admin/rules` - 新しいルールを作成
- `PUT /api/admin/rules/{id}` - ルールを更新
- `DELETE /api/admin/rules/{id}` - ルールを削除
- `GET /api/admin/questions` - すべての質問を取得
- `GET /api/admin/validate/{visa_type}` - 整合性チェックを実行

## トラブルシューティング

### ポートが使用中の場合

**バックエンド**:
```bash
# ポート8000が使用中の場合
uvicorn app.main:app --reload --port 8001
```

**フロントエンド**:
```bash
# ポート5173が使用中の場合、Viteが自動的に別のポートを使用
npm run dev
```

### データベースのリセット

```bash
cd backend
rm visa_expert.db  # SQLiteデータベースを削除
python migrate_rules.py  # 再度マイグレーション実行
```

## ライセンス

Private - All rights reserved

## 作成者

Expert System Development Team - 2025
