# ビザ選定エキスパートシステム v4.0

オブジェクト指向設計による前向き推論エンジンを使用したビザ選定診断システム

## 主な機能

### 診断機能
- Eビザ、Lビザ、Bビザなどの適性診断
- 一問一答形式の対話型診断
- リアルタイムの推論過程可視化
- 前の質問に戻る・やり直し機能

### 管理機能（新機能）
- ルールの追加・編集・削除
- 質問文の管理
- 整合性チェック（矛盾検出、循環参照検出、到達不可能ルール検出）
- 変更履歴の記録

## 技術スタック

### バックエンド
- FastAPI
- SQLAlchemy（ORM）
- PostgreSQL（本番）/ SQLite（開発）
- Pydantic

### フロントエンド
- React 18
- Vite
- React Router
- Tailwind CSS

## ローカル開発

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# データベース初期化とルール移行
python migrate_rules.py

# サーバー起動
uvicorn app.main:app --reload
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

## デプロイ（Render）

このリポジトリはRenderで自動デプロイされます。

### 必要な環境変数
- `DATABASE_URL`: PostgreSQLの接続URL（Renderが自動設定）
- `ADMIN_USERNAME`: 管理画面のユーザー名（デフォルト: admin）
- `ADMIN_PASSWORD`: 管理画面のパスワード（デフォルト: admin123）

## アーキテクチャ

### 推論エンジン
- 前向き推論（Forward Chaining）
- ルールベースの知識表現
- 導出可能な事実の自動判定

### データベース設計
- Rules: ルール本体
- Conditions: ルールの条件
- Questions: 質問マスタ
- RuleHistory: 変更履歴
- ValidationResult: 整合性チェック結果

## ライセンス

Private - All rights reserved
