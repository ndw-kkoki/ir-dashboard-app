"""
data_callbacks.py

データ表示関連のコールバック関数
"""

from dash.dependencies import Input, Output, State
from dash import dcc, html
from typing import Any, Tuple
import logging

from services.drive_service import DriveService
from components.data_card import DataCard


class DataCallbacks:
    """データ表示関連のコールバック機能を提供するクラス"""
    
    def __init__(self, app, drive_service: DriveService):
        """
        データコールバックの初期化
        
        Args:
            app: Dashアプリケーションインスタンス
            drive_service (DriveService): Google Driveサービス
        """
        self.app = app
        self.drive_service = drive_service
        self.logger = logging.getLogger(__name__)
        self.register_callbacks()
    
    def register_callbacks(self):
        """すべてのコールバックを登録"""
        self.register_spreadsheet_iframe_callbacks()
        self.register_download_button_callbacks()
        self.register_download_file_callbacks()
        self.register_reload_callbacks()
    
    def register_spreadsheet_iframe_callbacks(self):
        """スプレッドシートiframe表示コールバックを登録"""
        
        @self.app.callback(
            Output('segment-spreadsheet-iframe-container', 'children'),
            [Input('segment-ticker-dropdown', 'value'),
             Input('segment-header-dropdown', 'value')]
        )
        def update_segment_spreadsheet_iframe(selected_file_id, header_mode):
            """セグメントデータスプレッドシート表示を更新"""
            return self.create_spreadsheet_iframe(selected_file_id, header_mode)
        
        @self.app.callback(
            Output('revenue-spreadsheet-iframe-container', 'children'),
            [Input('revenue-ticker-dropdown', 'value'),
             Input('revenue-header-dropdown', 'value')]
        )
        def update_revenue_spreadsheet_iframe(selected_file_id, header_mode):
            """収益データスプレッドシート表示を更新"""
            return self.create_spreadsheet_iframe(selected_file_id, header_mode)
    
    def register_download_button_callbacks(self):
        """ダウンロードボタン有効/無効コールバックを登録"""
        
        @self.app.callback(
            [Output('segment-download-btn', 'disabled'),
             Output('revenue-download-btn', 'disabled')],
            [Input('segment-ticker-dropdown', 'value'),
             Input('revenue-ticker-dropdown', 'value')]
        )
        def update_download_button_state(segment_file_id, revenue_file_id):
            """ダウンロードボタンの有効/無効状態を更新"""
            segment_disabled = not bool(segment_file_id)
            revenue_disabled = not bool(revenue_file_id)
            return segment_disabled, revenue_disabled
    
    def register_download_file_callbacks(self):
        """ファイルダウンロードコールバックを登録"""
        
        @self.app.callback(
            Output("segment-download-xlsx", "data"),
            [Input("segment-download-btn", "n_clicks")],
            [State('segment-ticker-dropdown', 'value')]
        )
        def download_segment_file(n_clicks, selected_file_id):
            """セグメントデータファイルをダウンロード"""
            return self.download_file(n_clicks, selected_file_id, 'segment')
        
        @self.app.callback(
            Output("revenue-download-xlsx", "data"),
            [Input("revenue-download-btn", "n_clicks")],
            [State('revenue-ticker-dropdown', 'value')]
        )
        def download_revenue_file(n_clicks, selected_file_id):
            """収益データファイルをダウンロード"""
            return self.download_file(n_clicks, selected_file_id, 'revenue')
    
    def register_reload_callbacks(self):
        """スプレッドシート再読み込みコールバックを登録"""
        
        @self.app.callback(
            Output('segment-spreadsheet-iframe-container', 'children', allow_duplicate=True),
            [Input('segment-reload-btn', 'n_clicks')],
            [State('segment-ticker-dropdown', 'value'),
             State('segment-header-dropdown', 'value')],
            prevent_initial_call=True
        )
        def reload_segment_spreadsheet(n_clicks, selected_file_id, header_mode):
            """セグメントデータスプレッドシートを再読み込み"""
            if n_clicks and n_clicks > 0:
                self.logger.info(f"セグメントデータスプレッドシートを再読み込み中: {selected_file_id}")
                return self.create_spreadsheet_iframe(selected_file_id, header_mode)
            return self.create_spreadsheet_iframe(selected_file_id, header_mode)
        
        @self.app.callback(
            Output('revenue-spreadsheet-iframe-container', 'children', allow_duplicate=True),
            [Input('revenue-reload-btn', 'n_clicks')],
            [State('revenue-ticker-dropdown', 'value'),
             State('revenue-header-dropdown', 'value')],
            prevent_initial_call=True
        )
        def reload_revenue_spreadsheet(n_clicks, selected_file_id, header_mode):
            """収益データスプレッドシートを再読み込み"""
            if n_clicks and n_clicks > 0:
                self.logger.info(f"収益データスプレッドシートを再読み込み中: {selected_file_id}")
                return self.create_spreadsheet_iframe(selected_file_id, header_mode)
            return self.create_spreadsheet_iframe(selected_file_id, header_mode)
    
    def create_spreadsheet_iframe(self, selected_file_id: str, header_mode: str) -> Any:
        """
        スプレッドシートiframeを作成
        
        Args:
            selected_file_id (str): 選択されたファイルID
            header_mode (str): ヘッダー表示モード
            
        Returns:
            Any: iframe要素またはエラーメッセージ
        """
        if not selected_file_id:
            return html.P("ファイルを選択してください", style={'color': '#666', 'fontSize': '16px'})
        
        try:
            # DataCardのcreate_iframe_elementメソッドを使用
            data_card = DataCard('temp', {})
            return data_card.create_iframe_element(selected_file_id, header_mode)
        except Exception as e:
            self.logger.error(f"iframe作成エラー: {e}")
            return html.Div([
                html.P("エラーが発生しました", style={'color': 'red', 'fontSize': '16px'}),
                html.P(f"詳細: {str(e)}", style={'color': '#666', 'fontSize': '12px'})
            ])
    
    def download_file(self, n_clicks: int, selected_file_id: str, file_type: str) -> Any:
        """
        ファイルをダウンロード
        
        Args:
            n_clicks (int): ボタンクリック回数
            selected_file_id (str): 選択されたファイルID
            file_type (str): ファイルタイプ ('segment' または 'revenue')
            
        Returns:
            Any: ダウンロードデータまたは更新なし
        """
        from dash import no_update
        
        if n_clicks <= 0 or not selected_file_id or not self.drive_service.is_connected():
            return no_update
        
        try:
            # ファイルコンテンツをダウンロード
            file_content = self.drive_service.download_file_content(selected_file_id)
            if not file_content:
                self.logger.error(f"ファイルダウンロードに失敗: {selected_file_id}")
                return no_update
            
            # ファイル名をファイルタイプとIDから生成（拡張子は.xlsx固定）
            filename = f"{file_type}_data_{selected_file_id[:8]}.xlsx"
            
            return dcc.send_bytes(file_content, filename)
            
        except Exception as e:
            self.logger.error(f"ダウンロードエラー: {e}")
            return no_update
