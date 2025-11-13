"""
file_callbacks.py

ファイル関連のコールバック関数
"""

from dash.dependencies import Input, Output
from dash import html
from typing import Any, Tuple, List, Dict
import logging

from services.drive_service import DriveService
from services.file_service import FileService
from components.ai_summary_card import AISummaryCard


class FileCallbacks:
    """ファイル関連のコールバック機能を提供するクラス"""
    
    def __init__(self, app, drive_service: DriveService):
        """
        ファイルコールバックの初期化
        
        Args:
            app: Dashアプリケーションインスタンス
            drive_service (DriveService): Google Driveサービス
        """
        self.app = app
        self.drive_service = drive_service
        self.file_service = FileService()
        self.logger = logging.getLogger(__name__)
        self.register_callbacks()
    
    def register_callbacks(self):
        """すべてのコールバックを登録"""
        self.register_drive_files_callback()
        self.register_ai_summary_callback()
    
    def register_drive_files_callback(self):
        """Google Driveファイル一覧取得コールバックを登録"""
        
        @self.app.callback(
            [Output('segment-ticker-dropdown', 'options'),
             Output('revenue-ticker-dropdown', 'options'),
             Output('ai-summary-file-dropdown', 'options'),
             Output('segment-ticker-dropdown', 'value'),
             Output('revenue-ticker-dropdown', 'value'),
             Output('ai-summary-file-dropdown', 'value')],
            Input('draggable', 'id'),  # アプリ起動時のトリガー
            prevent_initial_call=False
        )
        def load_drive_files_async(_):
            """Google Driveファイル一覧を非同期で取得"""
            return self.handle_drive_files_loading()
    
    def register_ai_summary_callback(self):
        """AI要約テキスト表示コールバックを登録"""
        
        @self.app.callback(
            Output('ai-summary-text-container', 'children'),
            [Input('ai-summary-file-dropdown', 'value'),
             Input('ai-summary-font-size-dropdown', 'value')]
        )
        def update_ai_summary_text(selected_file_id, font_size):
            """AI要約テキスト表示を更新"""
            return self.handle_ai_summary_update(selected_file_id, font_size)
    
    def handle_drive_files_loading(self) -> Tuple[List[Dict], List[Dict], List[Dict], str, str, str]:
        """
        Google Driveファイル読み込み処理
        
        Returns:
            Tuple: (セグメントオプション, 収益オプション, AI要約オプション, セグメントデフォルト, 収益デフォルト, AI要約デフォルト)
        """
        if not self.drive_service.is_connected():
            return [], [], [], None, None, None
        
        try:
            # settings.pyから設定をインポート
            from config.app_config import AppConfig
            
            folder_ids = {
                'segment': AppConfig.SEGMENT_DATA_FOLDER_ID,
                'revenue': AppConfig.REVENUE_OVERVIEW_FOLDER_ID,
                'ai_summary': AppConfig.AI_SUMMARY_FOLDER_ID
            }
            
            # ファイルを並列取得
            segment_files, revenue_files, ai_summary_files = self.drive_service.load_files_async(folder_ids)
            
            # ドロップダウンオプションを作成
            segment_options, segment_default = self.drive_service.get_dropdown_options(segment_files)
            revenue_options, revenue_default = self.drive_service.get_dropdown_options(revenue_files)
            ai_summary_options, ai_summary_default = self.drive_service.get_dropdown_options(ai_summary_files)
            
            self.logger.info(f"ファイル読み込み完了: セグメント{len(segment_options)}件, 収益{len(revenue_options)}件, AI要約{len(ai_summary_options)}件")
            
            return (
                segment_options, revenue_options, ai_summary_options,
                segment_default, revenue_default, ai_summary_default
            )
            
        except Exception as e:
            self.logger.error(f"ファイル読み込みエラー: {e}")
            return [], [], [], None, None, None
    
    def handle_ai_summary_update(self, selected_file_id: str, font_size: int) -> Any:
        """
        AI要約テキスト更新処理
        
        Args:
            selected_file_id (str): 選択されたファイルID
            font_size (int): フォントサイズ
            
        Returns:
            Any: テキスト要素またはエラーメッセージ
        """
        if not selected_file_id:
            return html.P("ファイルを選択してください", style={'color': '#666', 'fontSize': '16px'})
        
        try:
            # テキストファイルの内容を取得
            text_content = self.drive_service.download_text_content(selected_file_id)
            if text_content is None:
                return html.P("ファイルの読み込みに失敗しました", style={'color': 'red', 'fontSize': '16px'})
            
            # AISummaryCardを使用してテキストをフォーマット
            ai_summary_card = AISummaryCard('ai-summary', {'title': 'AI要約', 'icon': '💡'})
            text_elements = ai_summary_card.format_text_content(text_content, font_size)
            
            return text_elements
            
        except Exception as e:
            self.logger.error(f"AI要約更新エラー: {e}")
            return html.Div([
                html.P("エラーが発生しました", style={'color': 'red', 'fontSize': '16px'}),
                html.P(f"詳細: {str(e)}", style={'color': '#666', 'fontSize': '12px'})
            ])
