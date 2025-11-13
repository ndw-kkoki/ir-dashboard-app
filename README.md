# Analysis Dashboard App

## 概要

Analysis Dashboard Appは、Google Driveに保存されたExcelファイルとテキストファイルを表示・分析するためのWebアプリケーションです。

## 改善点

### 1. モジュール分割とクラス化

- **責務の明確化**: 各機能を独立したクラスとモジュールに分離
- **再利用性の向上**: コンポーネントとサービスの再利用が容易
- **テスト容易性**: 個々のクラスの単体テストが可能

### 2. ディレクトリ構造

```bash
src/
├── app.py                  # メインファイル
├── app_manager.py          # アプリケーション管理クラス
├── components/             # UIコンポーネント
│   ├── __init__.py
│   ├── base_component.py   # 基底コンポーネントクラス
│   ├── data_card.py        # データ表示カード
│   ├── ai_summary_card.py  # AI要約カード
│   └── chatbot_card.py     # チャットボットカード
├── services/               # ビジネスロジック
│   ├── __init__.py
│   ├── chatbot_service.py  # チャットボット機能
│   ├── file_service.py     # ファイル操作
│   └── drive_service.py    # Google Drive操作
├── callbacks/              # Dashコールバック関数
│   ├── __init__.py
│   ├── data_callbacks.py   # データ関連コールバック
│   ├── chatbot_callbacks.py # チャット関連コールバック
│   └── file_callbacks.py   # ファイル関連コールバック
├── config/                 # 設定管理
│   ├── __init__.py
│   ├── app_config.py       # アプリケーション設定
│   └── layout_config.py    # レイアウト設定
└── utils/                  # ユーティリティ
    ├── __init__.py
    └── drive_xlsx_loader.py # Google Drive連携
```

### 3. 主要なクラス

#### AnalysisDashboardApp (app_manager.py)

- アプリケーション全体のライフサイクルを管理
- 設定の読み込みと検証
- コンポーネントとサービスの初期化
- コールバックの登録

#### コンポーネントクラス (components/)

- **BaseComponent**: 全UIコンポーネントの基底クラス
- **DataCard**: スプレッドシート表示カード
- **AISummaryCard**: AI要約テキスト表示カード
- **ChatbotCard**: チャットボット機能カード

#### サービスクラス (services/)

- **DriveService**: Google Drive操作を統括
- **ChatbotService**: チャットボット機能を提供
- **FileService**: ファイル操作ユーティリティ

#### コールバッククラス (callbacks/)

- **DataCallbacks**: データ表示関連のコールバック
- **ChatbotCallbacks**: チャットボット関連のコールバック
- **FileCallbacks**: ファイル関連のコールバック

#### 設定クラス (config/)

- **AppConfig**: アプリケーション設定の管理
- **LayoutConfig**: レイアウト設定の管理

## 使用方法

### アプリ起動

```python
# app_new.py を使用
python src/app_new.py
```

### カスタム設定での起動

```python
from app_manager import AnalysisDashboardApp
from config.app_config import AppConfig

# カスタム設定
config = AppConfig(
    DEBUG=False,
    HOST="0.0.0.0",
    PORT=5000
)

# アプリ起動
app = AnalysisDashboardApp(config=config)
app.run()
```

### 環境変数での設定

```bash
# 環境変数設定例
export DEBUG=False
export HOST=0.0.0.0
export PORT=5000
export CREDENTIALS_FILE=/path/to/credentials.json
export SEGMENT_DATA_FOLDER_ID=your_folder_id
```

## 主要な改善点詳細

### 1. 設定の外部化

- 環境変数からの設定読み込み
- 設定の妥当性検証
- デフォルト値の適切な管理

### 2. エラーハンドリングの強化

- 各層でのエラーハンドリング
- ログ出力の統一
- ユーザーフレンドリーなエラーメッセージ

### 3. パフォーマンスの最適化

- ファイル一覧の並列取得
- キャッシュ機能の活用
- 非同期処理の最適化

### 4. コードの品質向上

- 型ヒントの追加
- ドキュメント文字列の充実
- PEP8準拠のコード整理

### 5. テスタビリティの向上

- 依存関係の注入
- モックが容易な設計
- 単体テストが書きやすい構造

## 今後の拡張予定

### 1. 機能拡張

- 実際のAI連携（OpenAI GPT等）
- データ分析機能の追加
- ユーザー認証機能
- レポート生成機能

### 2. 技術改善

- キャッシュ層の強化
- データベース連携
- API化
- Docker対応

### 3. UI/UX改善

- カスタムテーマ機能
- ダークモード対応
- モバイル対応の強化
- アクセシビリティ向上

## 依存関係

元のアプリケーションと同じ依存関係を使用：

- dash
- dash-draggable
- google-api-python-client
- google-auth
- google-auth-httplib2
- google-auth-oauthlib
- pandas
- openpyxl
- gunicorn (本番環境用)

## GCPデプロイ手順

### 前提条件

1. **Google Cloud SDKのインストール**

   ```bash
   # Google Cloud SDKをインストール
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Google Cloudプロジェクトの準備**

   ```bash
   # Google Cloudにログイン
   gcloud auth login
   
   # プロジェクトを作成または選択
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **サービスアカウントの設定**

   ```bash
   # サービスアカウントを作成
   gcloud iam service-accounts create analysis-dashboard-sa \
       --display-name="Analysis Dashboard Service Account"
   
   # Google Drive APIアクセス権限を付与
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:analysis-dashboard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/editor"
   ```

### 認証設定

#### ローカル開発環境（OAuth認証）

1. **Google Cloud Consoleでの設定**
   - Google Drive APIを有効化
   - OAuth 2.0クライアントIDを作成
   - credentials.jsonをダウンロード

2. **環境変数の設定**

   ```bash
   export CREDENTIALS_FILE=path/to/credentials.json
   export USE_SERVICE_ACCOUNT=false
   export SEGMENT_DATA_FOLDER_ID=your_segment_folder_id
   export REVENUE_OVERVIEW_FOLDER_ID=your_revenue_folder_id
   export AI_SUMMARY_FOLDER_ID=your_ai_summary_folder_id
   ```

#### 本番環境（サービスアカウント認証）

1. **サービスアカウントキーの作成**

   ```bash
   # サービスアカウントキーを作成
   gcloud iam service-accounts keys create service-account-key.json \
       --iam-account=analysis-dashboard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

2. **環境変数の設定**

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
   export USE_SERVICE_ACCOUNT=true
   export DEBUG=false
   export HOST=0.0.0.0
   export PORT=8080
   ```

### デプロイ方法

#### 方法1: 自動デプロイスクリプト使用

**Linux/Mac:**

```bash
# スクリプトに実行権限を付与
chmod +x deploy.sh

# デプロイ実行
./deploy.sh YOUR_PROJECT_ID asia-northeast1
```

**Windows PowerShell:**

```powershell
# デプロイ実行
.\deploy.ps1 -ProjectId "YOUR_PROJECT_ID" -Region "asia-northeast1"
```

#### 方法2: 手動デプロイ

1. **必要なAPIの有効化**

   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable drive.googleapis.com
   ```

2. **Dockerイメージのビルド**

   ```bash
   # Dockerイメージをビルドしてプッシュ
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/analysis-dashboard-app
   ```

3. **Cloud Runへのデプロイ**

   ```bash
   gcloud run deploy analysis-dashboard-app \
       --image gcr.io/YOUR_PROJECT_ID/analysis-dashboard-app \
       --platform managed \
       --region asia-northeast1 \
       --allow-unauthenticated \
       --service-account analysis-dashboard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
       --set-env-vars "DEBUG=false,HOST=0.0.0.0,USE_SERVICE_ACCOUNT=true,SEGMENT_DATA_FOLDER_ID=your_folder_id,REVENUE_OVERVIEW_FOLDER_ID=your_folder_id,AI_SUMMARY_FOLDER_ID=your_folder_id" \
       --memory 2Gi \
       --cpu 1 \
       --max-instances 10 \
       --timeout 300
   ```

### Google Driveアクセス権限の設定

本番環境でGoogle Driveにアクセスするには、サービスアカウントに適切な権限を付与する必要があります：

1. **Google Drive共有設定**

   ```bash
   分析対象のGoogle Driveフォルダを、サービスアカウントのメールアドレス
   (analysis-dashboard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com) 
   と共有してください。
   ```

2. **フォルダIDの取得**

   ```bash
   Google DriveのフォルダURLから、フォルダIDを取得してください。
   例: https://drive.google.com/drive/folders/1ABC...XYZ
   フォルダID: 1ABC...XYZ
   ```

### 環境変数一覧

| 変数名 | 説明 | ローカル | 本番 |
|--------|------|----------|------|
| `DEBUG` | デバッグモード | `true` | `false` |
| `HOST` | ホストアドレス | `127.0.0.1` | `0.0.0.0` |
| `PORT` | ポート番号 | `8050` | `8080` |
| `USE_SERVICE_ACCOUNT` | サービスアカウント認証使用 | `false` | `true` |
| `CREDENTIALS_FILE` | 認証ファイルパス | `credentials.json` | 不要* |
| `GOOGLE_APPLICATION_CREDENTIALS` | サービスアカウントキーパス | 不要 | 設定済み** |
| `SEGMENT_DATA_FOLDER_ID` | セグメントデータフォルダID | 必須 | 必須 |
| `REVENUE_OVERVIEW_FOLDER_ID` | 収益データフォルダID | 必須 | 必須 |
| `AI_SUMMARY_FOLDER_ID` | AI要約データフォルダID | 必須 | 必須 |

\* Cloud Runでは自動的にサービスアカウントが使用されます  
\** Cloud Runのサービスアカウント設定により自動設定されます

### トラブルシューティング

#### 認証エラー

```bash
Google Drive API認証エラーが発生した場合:
1. サービスアカウントが正しく作成されているか確認
2. Google Drive APIが有効化されているか確認
3. フォルダがサービスアカウントと共有されているか確認
```

#### デプロイエラー

```bash
Cloud Runデプロイエラーが発生した場合:
1. プロジェクトIDが正しいか確認
2. 必要なAPIが有効化されているか確認
3. 適切な権限があるか確認
```

#### 接続エラー

```bash
アプリケーション実行時にエラーが発生した場合:
1. 環境変数が正しく設定されているか確認
2. フォルダIDが正しいか確認
3. ログを確認して詳細なエラー情報を取得
```

#### CORSエラー / iframe表示エラー

```bash
Google Sheetsのiframe表示でCORSエラーが発生した場合:

1. CORS設定の確認:
   - flask-corsライブラリが正常にインストールされているか確認
   - アプリケーションでCORS設定が適用されているか確認

2. Google Sheetsの共有設定:
   - スプレッドシートが適切に共有されているか確認
   - サービスアカウントに閲覧権限があるか確認

3. ブラウザのセキュリティ設定:
   - ブラウザのCORS設定を確認
   - 開発者モードでコンソールエラーを確認

4. 本番環境での対策:
   - CORS_ORIGINSを適切なドメインに設定
   - HTTPSを使用してセキュアな接続を確保

注意: 社内ドキュメントのため、Google Sheetsの編集可能リンクのみを使用します。
```

## ライセンス

MIT License
