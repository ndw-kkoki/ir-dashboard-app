"""
app_config.py

アプリケーション設定クラス
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass


def load_env_file(env_file_path: str = ".env"):
    """
    .envファイルから環境変数を読み込む
    
    Args:
        env_file_path (str): .envファイルのパス
    """
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 既存の環境変数を上書きしない
                    if key not in os.environ:
                        os.environ[key] = value


@dataclass
class AppConfig:
    """アプリケーション設定クラス"""
    
    # アプリ基本設定
    APP_NAME: str = "Analysis Dashboard App"
    APP_ICON: str = "📊"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8050
    
    # Google Drive 設定
    CREDENTIALS_FILE: str = os.environ.get("CREDENTIALS_FILE", "credentials.json")
    TOKEN_FILE: str = "token.json"
    USE_SERVICE_ACCOUNT: bool = os.environ.get("USE_SERVICE_ACCOUNT", "false").lower() == "true"
    
    # Google Drive フォルダID
    SEGMENT_DATA_FOLDER_ID: str = os.environ.get("SEGMENT_DATA_FOLDER_ID", "")
    REVENUE_OVERVIEW_FOLDER_ID: str = os.environ.get("REVENUE_OVERVIEW_FOLDER_ID", "")
    AI_SUMMARY_FOLDER_ID: str = os.environ.get("AI_SUMMARY_FOLDER_ID", "")

    # フォントサイズ設定
    FONT_SIZE_OPTIONS: List[Dict[str, Any]] = None
    DEFAULT_FONT_SIZE: int = 14
    
    # チャットボット設定
    CHATBOT_PLACEHOLDER: str = "表示中のデータについて質問してください..."
    CHATBOT_MAX_HISTORY: int = 10
    
    # カード設定
    CARD_STYLES: Dict[str, Dict[str, str]] = None
    
    # 外部スタイルシート
    EXTERNAL_STYLESHEETS: List[str] = None
    
    # CORS設定
    CORS_ORIGINS: List[str] = None
    CORS_ALLOW_HEADERS: List[str] = None
    CORS_METHODS: List[str] = None
    
    # iframe設定
    IFRAME_SANDBOX_ATTRIBUTES: str = "allow-scripts allow-same-origin allow-popups allow-forms"
    
    def __post_init__(self):
        """初期化後の設定"""
        if self.FONT_SIZE_OPTIONS is None:
            self.FONT_SIZE_OPTIONS = [
                {'label': '8px', 'value': 8},
                {'label': '10px', 'value': 10},
                {'label': '12px', 'value': 12},
                {'label': '14px', 'value': 14},
                {'label': '16px', 'value': 16},
                {'label': '18px', 'value': 18},
                {'label': '20px', 'value': 20},
                {'label': '24px', 'value': 24},
                {'label': '28px', 'value': 28},
                {'label': '32px', 'value': 32}
            ]
        
        if self.CARD_STYLES is None:
            self.CARD_STYLES = {
                "segment_data": {
                    "title": "セグメントデータ",
                    "icon": "📈"
                },
                "earnings_overview": {
                    "title": "収益動向の概要", 
                    "icon": "💰"
                },
                "ai_summary": {
                    "title": "AIによる収益動向の要約",
                    "icon": "💡"
                },
                "chatbot": {
                    "title": "チャットボット",
                    "icon": "💬"
                }
            }
        
        if self.EXTERNAL_STYLESHEETS is None:
            self.EXTERNAL_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
            
        if self.CORS_ORIGINS is None:
            self.CORS_ORIGINS = ["*"]
            
        if self.CORS_ALLOW_HEADERS is None:
            self.CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
            
        if self.CORS_METHODS is None:
            self.CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """
        環境変数から設定を読み込み（.envファイルも読み込む）
        
        Returns:
            AppConfig: 設定インスタンス
        """
        # .envファイルを読み込み
        load_env_file()
        
        return cls(
            DEBUG=os.environ.get("DEBUG", "True").lower() == "true",
            HOST=os.environ.get("HOST", "127.0.0.1"),
            PORT=int(os.environ.get("PORT", "8050")),
            CREDENTIALS_FILE=os.environ.get("CREDENTIALS_FILE", "credentials.json"),
            TOKEN_FILE=os.environ.get("TOKEN_FILE", "token.json"),
            USE_SERVICE_ACCOUNT=os.environ.get("USE_SERVICE_ACCOUNT", "false").lower() == "true",
            SEGMENT_DATA_FOLDER_ID=os.environ.get("SEGMENT_DATA_FOLDER_ID", ""),
            REVENUE_OVERVIEW_FOLDER_ID=os.environ.get("REVENUE_OVERVIEW_FOLDER_ID", ""),
            AI_SUMMARY_FOLDER_ID=os.environ.get("AI_SUMMARY_FOLDER_ID", ""),
            DEFAULT_FONT_SIZE=int(os.environ.get("DEFAULT_FONT_SIZE", "14")),
            CHATBOT_MAX_HISTORY=int(os.environ.get("CHATBOT_MAX_HISTORY", "10"))
        )
    
    def get_chatbot_responses(self) -> List[str]:
        """
        チャットボット定型文レスポンスを取得
        
        Returns:
            List[str]: レスポンスのリスト
        """
        return [
            "ご質問をお聞きしました。現在のデータを分析中です...",
            "興味深い視点ですね。表示されているデータから詳しい分析結果をお伝えします。",
            "データを確認したところ、いくつかのポイントが見つかりました。",
            "ご質問の内容について、チャートとデータから読み取れる情報をお答えします。",
            "分析結果をお伝えします。データの傾向から以下の点が注目されます。",
            "このデータに関して、重要な洞察をお共有します。",
            "ご質問ありがとうございます。現在表示中のデータから判断すると...",
            "データ分析の観点から、以下のような見解をお示しします。",
            "チャートの傾向を見ると、興味深いパターンが見受けられます。",
            "ご指摘の点について、データから読み取れる情報をお答えします。"
        ]
    
    def validate(self) -> bool:
        """
        設定の妥当性を検証
        
        Returns:
            bool: 設定が妥当な場合True
        """
        # 必須ファイルの存在確認
        if not os.path.exists(self.CREDENTIALS_FILE):
            print(f"警告: 認証ファイルが見つかりません: {self.CREDENTIALS_FILE}")
            return False
        
        # ポート番号の妥当性確認
        if not (1 <= self.PORT <= 65535):
            print(f"エラー: 無効なポート番号: {self.PORT}")
            return False
        
        # フォルダIDの妥当性確認
        folder_ids = [
            self.SEGMENT_DATA_FOLDER_ID,
            self.REVENUE_OVERVIEW_FOLDER_ID,
            self.AI_SUMMARY_FOLDER_ID
        ]
        
        for folder_id in folder_ids:
            if not folder_id or len(folder_id) < 10:
                print(f"警告: 無効なフォルダID: {folder_id}")
        
        return True
