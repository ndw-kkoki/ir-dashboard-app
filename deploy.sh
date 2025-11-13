#!/bin/bash

# Google Cloud Platformへのデプロイスクリプト
# 使用方法: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# デフォルト値
DEFAULT_PROJECT_ID="your-project-id"
DEFAULT_REGION="asia-northeast1"

# パラメータの設定
PROJECT_ID=${1:-$DEFAULT_PROJECT_ID}
REGION=${2:-$DEFAULT_REGION}
APP_NAME="analysis-dashboard-app"
SERVICE_ACCOUNT_NAME="analysis-dashboard-sa"

echo "🚀 Google Cloud Run へのデプロイを開始します..."
echo "プロジェクトID: $PROJECT_ID"
echo "リージョン: $REGION"
echo "アプリ名: $APP_NAME"

# Google Cloud プロジェクトの設定
echo "📋 Google Cloud プロジェクトを設定中..."
gcloud config set project $PROJECT_ID

# 必要なAPIの有効化
echo "🔧 必要なAPIを有効化中..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable drive.googleapis.com

# サービスアカウントの作成（存在しない場合）
echo "👤 サービスアカウントを設定中..."
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com >/dev/null 2>&1; then
    echo "サービスアカウントを作成中..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Analysis Dashboard Service Account" \
        --description="Service account for Analysis Dashboard App"
    
    # Google Drive アクセス権限を付与（必要に応じて調整）
    echo "サービスアカウントに権限を付与中..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/editor"
else
    echo "サービスアカウントは既に存在します。"
fi

# Dockerイメージのビルドとプッシュ
echo "🏗️ Dockerイメージをビルド中..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME

# Cloud Run へのデプロイ
echo "🚢 Cloud Run にデプロイ中..."
gcloud run deploy $APP_NAME \
    --image gcr.io/$PROJECT_ID/$APP_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --service-account ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
    --set-env-vars "DEBUG=false,HOST=0.0.0.0,USE_SERVICE_ACCOUNT=true" \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 300

echo "✅ デプロイが完了しました！"
echo ""
echo "🌐 アプリケーションURL:"
gcloud run services describe $APP_NAME --region $REGION --format 'value(status.url)'
echo ""
echo "📝 次のステップ:"
echo "1. Google Drive のフォルダIDを環境変数に設定してください"
echo "2. サービスアカウントに Google Drive の適切なアクセス権限を付与してください"
echo "3. 必要に応じて認証設定を確認してください"
