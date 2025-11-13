# Google Cloud Platformへのデプロイスクリプト (PowerShell版)
# 使用方法: .\deploy.ps1 [PROJECT_ID] [REGION]

param(
    [string]$ProjectId = "your-project-id",
    [string]$Region = "asia-northeast1"
)

$ErrorActionPreference = "Stop"

# デフォルト値
$AppName = "analysis-dashboard-app"
$ServiceAccountName = "analysis-dashboard-sa"

Write-Host "🚀 Google Cloud Run へのデプロイを開始します..." -ForegroundColor Green
Write-Host "プロジェクトID: $ProjectId" -ForegroundColor Cyan
Write-Host "リージョン: $Region" -ForegroundColor Cyan
Write-Host "アプリ名: $AppName" -ForegroundColor Cyan

# Google Cloud プロジェクトの設定
Write-Host "📋 Google Cloud プロジェクトを設定中..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# 必要なAPIの有効化
Write-Host "🔧 必要なAPIを有効化中..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable drive.googleapis.com

# サービスアカウントの作成（存在しない場合）
Write-Host "👤 サービスアカウントを設定中..." -ForegroundColor Yellow
$ServiceAccountEmail = "$ServiceAccountName@$ProjectId.iam.gserviceaccount.com"

try {
    gcloud iam service-accounts describe $ServiceAccountEmail | Out-Null
    Write-Host "サービスアカウントは既に存在します。" -ForegroundColor Green
}
catch {
    Write-Host "サービスアカウントを作成中..." -ForegroundColor Yellow
    gcloud iam service-accounts create $ServiceAccountName `
        --display-name="Analysis Dashboard Service Account" `
        --description="Service account for Analysis Dashboard App"
    
    # Google Drive アクセス権限を付与（必要に応じて調整）
    Write-Host "サービスアカウントに権限を付与中..." -ForegroundColor Yellow
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$ServiceAccountEmail" `
        --role="roles/editor"
}

# Dockerイメージのビルドとプッシュ
Write-Host "🏗️ Dockerイメージをビルド中..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$ProjectId/$AppName

# Cloud Run へのデプロイ
Write-Host "🚢 Cloud Run にデプロイ中..." -ForegroundColor Yellow
gcloud run deploy $AppName `
    --image gcr.io/$ProjectId/$AppName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --service-account $ServiceAccountEmail `
    --set-env-vars "DEBUG=false,HOST=0.0.0.0,USE_SERVICE_ACCOUNT=true" `
    --memory 2Gi `
    --cpu 1 `
    --max-instances 10 `
    --timeout 300

Write-Host "✅ デプロイが完了しました！" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 アプリケーションURL:" -ForegroundColor Cyan
$AppUrl = gcloud run services describe $AppName --region $Region --format 'value(status.url)'
Write-Host $AppUrl -ForegroundColor White
Write-Host ""
Write-Host "📝 次のステップ:" -ForegroundColor Yellow
Write-Host "1. Google Drive のフォルダIDを環境変数に設定してください" -ForegroundColor White
Write-Host "2. サービスアカウントに Google Drive の適切なアクセス権限を付与してください" -ForegroundColor White
Write-Host "3. 必要に応じて認証設定を確認してください" -ForegroundColor White
