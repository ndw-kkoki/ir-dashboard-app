"""
app.py

Analysis Dashboard App のメインエントリーポイント
リファクタリング後の新しい構造を使用
"""

import os
from app_manager import AnalysisDashboardApp
from config.app_config import AppConfig


def main():
    """メイン関数"""
    # 環境に応じた設定を読み込み
    config = AppConfig.from_env()
    
    # 本番環境では debug=False, host と port を環境変数から取得
    debug_mode = config.DEBUG
    host = config.HOST
    port = int(os.environ.get('PORT', config.PORT))
    
    # アプリケーションインスタンスを作成
    dashboard_app = AnalysisDashboardApp(debug=debug_mode, config=config)
    
    # Google Drive接続状態をログ出力
    connection_status = dashboard_app.get_drive_connection_status()
    print(f"Google Drive接続状態: {connection_status}")
    
    # アプリケーションを実行
    if os.environ.get('GAE_ENV', '').startswith('standard'):
        # Google App Engine環境
        dashboard_app.run(host='0.0.0.0', port=port)
    elif os.environ.get('K_SERVICE'):
        # Google Cloud Run環境
        dashboard_app.run(host='0.0.0.0', port=port)
    else:
        # ローカル環境
        dashboard_app.run(host=host, port=port)


if __name__ == '__main__':
    main()
