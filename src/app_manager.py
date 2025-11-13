"""
app_manager.py

アプリケーション全体を管理するメインクラス
"""

import logging
import dash
import dash_draggable
from dash import html
from typing import Dict, Any
from flask_cors import CORS

from config.app_config import AppConfig
from config.layout_config import LayoutConfig
from services import DriveService, ChatbotService
from components import DataCard, AISummaryCard, ChatbotCard
from callbacks import DataCallbacks, ChatbotCallbacks, FileCallbacks


class AnalysisDashboardApp:
    """Analysis Dashboard Appのメインアプリケーションクラス"""
    
    def __init__(self, debug: bool = None, config: AppConfig = None):
        """
        アプリケーションの初期化
        
        Args:
            debug (bool): デバッグモード
            config (AppConfig): アプリケーション設定
        """
        # 設定の初期化
        self.config = config or AppConfig.from_env()
        self.layout_config = LayoutConfig()
        
        # デバッグモードの設定
        self.debug = debug if debug is not None else self.config.DEBUG
        
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 設定の妥当性確認
        if not self.config.validate():
            self.logger.warning("設定に問題があります。アプリケーションが正常に動作しない可能性があります。")
        
        # Dashアプリの初期化
        self.app = dash.Dash(
            __name__, 
            external_stylesheets=self.config.EXTERNAL_STYLESHEETS
        )
        
        # CORSの設定を追加
        CORS(self.app.server, 
             origins=self.config.CORS_ORIGINS,
             allow_headers=self.config.CORS_ALLOW_HEADERS,
             methods=self.config.CORS_METHODS)
        
        # iframe埋め込みを許可するためのヘッダー設定
        @self.app.server.after_request
        def after_request(response):
            response.headers['X-Frame-Options'] = 'ALLOWALL'
            response.headers['Content-Security-Policy'] = 'frame-ancestors *'
            return response
        
        # サービスの初期化
        self.drive_service = DriveService(
            self.config.CREDENTIALS_FILE, 
            self.config.TOKEN_FILE,
            self.config.USE_SERVICE_ACCOUNT
        )
        self.chatbot_service = ChatbotService(self.config.get_chatbot_responses())
        
        # コンポーネントの初期化
        self.components = self.initialize_components()
        
        # レイアウトの設定
        self.setup_layout()
        
        # コールバックの登録
        self.register_callbacks()
        
        self.logger.info("Analysis Dashboard App初期化完了")
    
    def setup_logging(self):
        """ログ設定のセットアップ"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def initialize_components(self) -> Dict[str, Any]:
        """
        コンポーネントの初期化
        
        Returns:
            Dict[str, Any]: 初期化されたコンポーネント辞書
        """
        # 初期は空のオプション（後でコールバックで更新）
        empty_options = []
        
        components = {
            'segment_card': DataCard(
                component_id='segment',
                config={
                    **self.config.CARD_STYLES['segment_data'],
                    'card_type': 'segment',
                    'file_label': 'ティッカーファイル:'
                },
                file_options=empty_options
            ),
            'revenue_card': DataCard(
                component_id='revenue',
                config={
                    **self.config.CARD_STYLES['earnings_overview'],
                    'card_type': 'revenue',
                    'file_label': '収益データファイル:'
                },
                file_options=empty_options
            ),
            'ai_summary_card': AISummaryCard(
                component_id='ai-summary',
                config=self.config.CARD_STYLES['ai_summary'],
                file_options=empty_options,
                font_size_options=self.config.FONT_SIZE_OPTIONS,
                default_font_size=self.config.DEFAULT_FONT_SIZE
            ),
            'chatbot_card': ChatbotCard(
                component_id='chatbot',
                config=self.config.CARD_STYLES['chatbot'],
                font_size_options=self.config.FONT_SIZE_OPTIONS,
                default_font_size=self.config.DEFAULT_FONT_SIZE,
                placeholder=self.config.CHATBOT_PLACEHOLDER,
                max_history=self.config.CHATBOT_MAX_HISTORY
            )
        }
        
        return components
    
    def setup_layout(self):
        """レイアウトのセットアップ"""
        self.app.layout = html.Div([
            # タイトル
            html.H3(self.config.APP_NAME, style={'margin': '5px 0', 'textAlign': 'center'}),
            
            # レスポンシブグリッドレイアウト
            dash_draggable.ResponsiveGridLayout(
                id='draggable',
                children=[
                    self.components['segment_card'].render(),
                    self.components['revenue_card'].render(),
                    self.components['ai_summary_card'].render(),
                    self.components['chatbot_card'].render()
                ],
                **self.layout_config.get_responsive_props()
            )
        ])
    
    def get_grid_layouts(self) -> Dict[str, list]:
        """
        グリッドレイアウト設定を取得（非推奨）
        
        Returns:
            Dict[str, list]: レイアウト設定
        """
        # 新しいLayoutConfigを使用
        return self.layout_config.GRID_LAYOUTS
    
    def register_callbacks(self):
        """コールバックの登録"""
        try:
            # データ関連コールバック
            self.data_callbacks = DataCallbacks(self.app, self.drive_service)
            
            # チャットボット関連コールバック
            self.chatbot_callbacks = ChatbotCallbacks(self.app, self.chatbot_service)
            
            # ファイル関連コールバック
            self.file_callbacks = FileCallbacks(self.app, self.drive_service)
            
            self.logger.info("コールバック登録完了")
            
        except Exception as e:
            self.logger.error(f"コールバック登録エラー: {e}")
            raise
    
    def run(self, host: str = None, port: int = None):
        """
        アプリケーションの実行
        
        Args:
            host (str): ホストアドレス
            port (int): ポート番号
        """
        # 設定から値を取得、引数が指定されていればそれを優先
        host = host or self.config.HOST
        port = port or self.config.PORT
        
        self.logger.info(f"Analysis Dashboard App起動中... http://{host}:{port}")
        self.logger.info(f"デバッグモード: {self.debug}")
        self.app.run(debug=self.debug, host=host, port=port)
    
    def get_app(self):
        """
        Dashアプリインスタンスを取得
        
        Returns:
            dash.Dash: Dashアプリインスタンス
        """
        return self.app
    
    def get_drive_connection_status(self) -> Dict[str, str]:
        """
        Google Drive接続状態を取得
        
        Returns:
            Dict[str, str]: 接続状態情報
        """
        return self.drive_service.get_connection_info()
