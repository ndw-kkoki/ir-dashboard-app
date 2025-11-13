# Analysis Dashboard App 環境変数設定スクリプト
# このスクリプトを実行して必要な環境変数を設定してください

Write-Host "Analysis Dashboard App - 環境変数設定" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Google Drive フォルダID設定
Write-Host "`n1. Google Drive フォルダIDの設定" -ForegroundColor Yellow
Write-Host "以下のフォルダIDを設定してください:" -ForegroundColor White

# セグメントデータフォルダID
$segmentFolderId = Read-Host "セグメントデータフォルダID (SEGMENT_DATA_FOLDER_ID)"
if ($segmentFolderId) {
    [Environment]::SetEnvironmentVariable("SEGMENT_DATA_FOLDER_ID", $segmentFolderId, "User")
    Write-Host "✓ SEGMENT_DATA_FOLDER_ID を設定しました: $segmentFolderId" -ForegroundColor Green
}

# 収益概要フォルダID
$revenueFolderId = Read-Host "収益概要フォルダID (REVENUE_OVERVIEW_FOLDER_ID)"
if ($revenueFolderId) {
    [Environment]::SetEnvironmentVariable("REVENUE_OVERVIEW_FOLDER_ID", $revenueFolderId, "User")
    Write-Host "✓ REVENUE_OVERVIEW_FOLDER_ID を設定しました: $revenueFolderId" -ForegroundColor Green
}

# AI要約フォルダID
$aiSummaryFolderId = Read-Host "AI要約フォルダID (AI_SUMMARY_FOLDER_ID)"
if ($aiSummaryFolderId) {
    [Environment]::SetEnvironmentVariable("AI_SUMMARY_FOLDER_ID", $aiSummaryFolderId, "User")
    Write-Host "✓ AI_SUMMARY_FOLDER_ID を設定しました: $aiSummaryFolderId" -ForegroundColor Green
}

# 認証ファイル設定（オプション）
Write-Host "`n2. Google Drive認証設定" -ForegroundColor Yellow
$useServiceAccount = Read-Host "サービスアカウントを使用しますか？ (y/N)"
if ($useServiceAccount -eq "y" -or $useServiceAccount -eq "Y") {
    [Environment]::SetEnvironmentVariable("USE_SERVICE_ACCOUNT", "true", "User")
    
    $credentialsFile = Read-Host "サービスアカウントキーファイルのパス (CREDENTIALS_FILE)"
    if ($credentialsFile -and (Test-Path $credentialsFile)) {
        [Environment]::SetEnvironmentVariable("CREDENTIALS_FILE", $credentialsFile, "User")
        [Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", $credentialsFile, "User")
        Write-Host "✓ サービスアカウント認証を設定しました" -ForegroundColor Green
    } else {
        Write-Host "⚠ 指定されたファイルが見つかりません" -ForegroundColor Yellow
    }
} else {
    [Environment]::SetEnvironmentVariable("USE_SERVICE_ACCOUNT", "false", "User")
    Write-Host "✓ OAuth認証を設定しました" -ForegroundColor Green
}

# 現在の環境変数確認
Write-Host "`n3. 設定された環境変数の確認" -ForegroundColor Yellow
Write-Host "SEGMENT_DATA_FOLDER_ID: $([Environment]::GetEnvironmentVariable('SEGMENT_DATA_FOLDER_ID', 'User'))" -ForegroundColor White
Write-Host "REVENUE_OVERVIEW_FOLDER_ID: $([Environment]::GetEnvironmentVariable('REVENUE_OVERVIEW_FOLDER_ID', 'User'))" -ForegroundColor White
Write-Host "AI_SUMMARY_FOLDER_ID: $([Environment]::GetEnvironmentVariable('AI_SUMMARY_FOLDER_ID', 'User'))" -ForegroundColor White
Write-Host "USE_SERVICE_ACCOUNT: $([Environment]::GetEnvironmentVariable('USE_SERVICE_ACCOUNT', 'User'))" -ForegroundColor White
Write-Host "CREDENTIALS_FILE: $([Environment]::GetEnvironmentVariable('CREDENTIALS_FILE', 'User'))" -ForegroundColor White

Write-Host "`n設定完了！" -ForegroundColor Green
Write-Host "変更を反映するために新しいPowerShellセッションを開始してください。" -ForegroundColor Yellow
Write-Host "または、以下のコマンドで現在のセッションで環境変数を更新してください:" -ForegroundColor Yellow
Write-Host 'refreshenv' -ForegroundColor Cyan

# 設定確認用の関数
Write-Host "`n設定確認のために、以下のコマンドを実行してください:" -ForegroundColor Yellow
Write-Host 'python -c "from config.app_config import AppConfig; config = AppConfig.from_env(); print(f\"設定確認: {config.validate()}\")"' -ForegroundColor Cyan
