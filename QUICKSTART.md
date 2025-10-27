# ビザ選定エキスパートシステム v4 - クイックスタートガイド

このガイドでは、最速でシステムを起動する手順を説明します。

## 🚀 5分で起動

### Windows環境の場合

#### 1. バックエンドの起動

```powershell
# プロジェクトのバックエンドディレクトリに移動
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\backend

# 仮想環境を作成（初回のみ）
python -m venv venv

# 仮想環境を有効化
venv\Scripts\activate

# 依存パッケージをインストール（初回のみ）
pip install -r requirements.txt

# データベースを初期化してルールを移行（初回のみ）
python migrate_rules.py

# サーバーを起動
uvicorn app.main:app --reload
```

成功すると、以下のように表示されます:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

#### 2. フロントエンドの起動

**新しいターミナルを開いて**以下を実行:

```powershell
# フロントエンドディレクトリに移動
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\frontend

# 依存パッケージをインストール（初回のみ）
npm install

# 開発サーバーを起動
npm run dev
```

成功すると、以下のように表示されます:
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:5173/
```

#### 3. ブラウザでアクセス

ブラウザで以下のURLを開きます:
```
http://localhost:5173
```

## 📋 2回目以降の起動

### バックエンド

```powershell
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### フロントエンド

```powershell
cd C:\Users\GPC999\Documents\works\visa-expert-system-v4\frontend
npm run dev
```

## 🎯 使い方

### 診断を実行

1. トップ画面で診断したいビザタイプ（E、L、B）を選択
2. 質問に「はい」「いいえ」で回答
3. 右側の画面で推論過程をリアルタイムで確認
4. 診断完了時に適用可能なビザが表示される

### 管理画面にアクセス

1. トップ画面右上の「管理画面」ボタンをクリック
2. 認証情報を入力:
   - ユーザー名: `admin`
   - パスワード: `admin123`
3. 以下の機能が利用可能:
   - **ルール管理**: ルールの追加・編集・削除
   - **質問管理**: 質問文の編集
   - **整合性チェック**: ルールの矛盾や問題を検出

## ❗ よくあるエラーと対処法

### エラー1: "Port 8000 is already in use"

**原因**: ポート8000が既に使用中

**対処法**: 別のポートを使用
```bash
uvicorn app.main:app --reload --port 8001
```
その場合、フロントエンドの`.env`ファイルも更新:
```
VITE_API_URL=http://localhost:8001/api
```

### エラー2: "Cannot find module 'react'"

**原因**: npm のパッケージがインストールされていない

**対処法**:
```bash
cd frontend
npm install
```

### エラー3: "No module named 'fastapi'"

**原因**: Python の仮想環境が有効化されていない、または依存関係がインストールされていない

**対処法**:
```bash
cd backend
venv\Scripts\activate  # 仮想環境を有効化
pip install -r requirements.txt
```

### エラー4: データベースエラー

**原因**: データベースファイルが壊れている

**対処法**: データベースを削除して再作成
```bash
cd backend
del visa_expert.db
python migrate_rules.py
```

## 🔧 開発時のヒント

### APIドキュメントの確認

バックエンドが起動している状態で、以下のURLにアクセス:
```
http://localhost:8000/docs
```
FastAPIの自動生成ドキュメントでAPIをテストできます。

### データベースの内容を確認

SQLiteデータベースは以下の場所にあります:
```
backend/visa_expert.db
```

[DB Browser for SQLite](https://sqlitebrowser.org/) などのツールで開いて内容を確認できます。

### ログの確認

- **バックエンド**: ターミナルにリアルタイムで表示
- **フロントエンド**: ブラウザの開発者ツール（F12）のコンソールタブ

## 📞 サポート

問題が解決しない場合は、以下を確認:

1. Python バージョン: `python --version` (3.8以上が必要)
2. Node.js バージョン: `node --version` (16以上が必要)
3. 仮想環境が有効化されているか確認

---

以上で起動完了です！診断を開始して、システムの動作を確認してください。
