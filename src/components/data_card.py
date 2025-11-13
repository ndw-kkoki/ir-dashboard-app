"""
data_card.py

データ表示カードコンポーネント（セグメントデータ、収益データ用）
"""

from dash import html, dcc
from typing import List, Dict
from .base_component import BaseComponent


class DataCard(BaseComponent):
    """データ表示カード（スプレッドシート）コンポーネント"""
    
    def __init__(self, component_id: str, config: dict, file_options: List[Dict] = None):
        """
        データカードの初期化
        
        Args:
            component_id (str): コンポーネントID
            config (dict): コンポーネント設定
            file_options (List[Dict]): ファイル選択オプション
        """
        super().__init__(component_id, config)
        self.file_options = file_options or []
        self.card_type = config.get('card_type', 'data')
        self.file_label = config.get('file_label', 'ファイル:')
    
    def render(self) -> html.Div:
        """
        データカードをレンダリング
        
        Returns:
            html.Div: レンダリングされたコンポーネント
        """
        return html.Div([
            html.Div([
                self.create_header(),
                self.create_content_area()
            ], style=self.create_container_style())
        ], style={'width': '100%', 'height': '100%'})
    
    def create_controls(self) -> html.Div:
        """
        コントロール部分を作成
        
        Returns:
            html.Div: コントロール要素
        """
        return html.Div([
            # ファイル選択
            html.Div([
                html.Label(self.file_label, style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    options=self.file_options,
                    value=self.file_options[0]['value'] if self.file_options else None,
                    id=f'{self.component_id}-ticker-dropdown',
                    placeholder="読み込み中...",
                    style={'marginBottom': '10px'}
                )
            ], style={'flex': '2', 'marginRight': '10px'}),
            
            # ヘッダー表示設定
            html.Div([
                html.Label("ヘッダー表示:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id=f'{self.component_id}-header-dropdown',
                    options=[
                        {'label': 'フル', 'value': 'none'},
                        {'label': '簡易表示', 'value': 'embedded'},
                        {'label': '表のみ', 'value': 'minimal'}
                    ],
                    value='embedded',
                    style={'marginBottom': '10px'}
                )
            ], style={'flex': '1', 'marginRight': '10px'}),
            
            # 再読み込みボタン
            html.Div([
                html.Label("　", style={'fontWeight': 'bold'}),  # スペーサー
                html.Button(
                    "リロード",
                    id=f'{self.component_id}-reload-btn',
                    n_clicks=0,
                    style=self.create_reload_button_style(),
                    disabled=False,
                    title="表示中のスプレッドシートを再読み込みします"
                )
            ], style={'flex': '0 0 120px', 'marginRight': '10px'}),
            
            # ダウンロードボタン
            html.Div([
                html.Label("　", style={'fontWeight': 'bold'}),  # スペーサー
                html.Button(
                    "ダウンロード",
                    id=f'{self.component_id}-download-btn',
                    n_clicks=0,
                    style=self.create_button_style(),
                    disabled=True,
                    title="表示中のスプレッドシートをExcel形式でダウンロードします"
                ),
                dcc.Download(id=f"{self.component_id}-download-xlsx")
            ], style={'flex': '0 0 150px'})
        ], style={
            'display': 'flex', 
            'padding': '10px', 
            'backgroundColor': '#fdfdfd'
        })
    
    def create_content_area(self) -> html.Div:
        """
        コンテンツ表示エリアを作成
        
        Returns:
            html.Div: コンテンツエリア
        """
        return html.Div(
            id=f'{self.component_id}-spreadsheet-iframe-container',
            style={
                'flex': '1',
                'border': '1px solid #ddd',
                'borderRadius': '0 0 10px 10px',
                'backgroundColor': '#f9f9f9',
                'textAlign': 'center',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'margin': '0 10px 10px 10px'
            },
            children=[html.P("読み込み中...", style={'color': '#666', 'fontSize': '16px'})]
        )
    
    def create_button_style(self) -> dict:
        """
        ボタンのスタイルを作成
        
        Returns:
            dict: ボタンスタイル
        """
        return {
            'borderRadius': '5px',
            'padding': '8px 16px',
            'cursor': 'pointer',
            'fontSize': '14px',
            'width': '100%',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'backgroundColor': "#6484e2",
            'color': 'white',
            'border': 'none'
        }
    
    def create_reload_button_style(self) -> dict:
        """
        再読み込みボタンのスタイルを作成
        
        Returns:
            dict: 再読み込みボタンスタイル
        """
        return {
            'borderRadius': '5px',
            'padding': '8px 12px',
            'cursor': 'pointer',
            'fontSize': '14px',
            'width': '100%',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'backgroundColor': "#bbbbbb",
            'color': 'white',
            'border': 'none',
            'transition': 'background-color 0.3s ease'
        }
    
    def create_iframe_element(self, file_id: str, header_mode: str) -> html.Iframe:
        """
        iframeエレメントを作成
        
        Args:
            file_id (str): Google DriveファイルID
            header_mode (str): ヘッダー表示モード
            
        Returns:
            html.Iframe: iframe要素
        """
        import time
        
        if not file_id:
            return html.P("ファイルを選択してください", 
                         style={'color': '#666', 'fontSize': '16px'})
        
        # ヘッダーモードに応じてURLパラメータを設定
        header_params = {
            'embedded': 'rm=embedded',
            'minimal': 'rm=minimal',
            'none': ''
        }
        
        rm_param = header_params.get(header_mode, 'rm=embedded')
        # キャッシュ無効化のためのタイムスタンプを追加
        timestamp = str(int(time.time()))
        separator = '&' if rm_param else ''
        
        # Google Sheetsの編集可能リンクを使用
        iframe_url = f"https://docs.google.com/spreadsheets/d/{file_id}/edit?{rm_param}{separator}t={timestamp}&widget=true&headers=false#gid=0"
        
        return html.Iframe(
            src=iframe_url,
            style={
                'width': '100%',
                'height': '100%',
                'border': 'none',
                'borderRadius': '5px',
                # CORSエラーを防ぐための追加設定
                'allowfullscreen': True
            },
            # iframe要素にsandbox属性を追加（セキュリティ強化）
            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        )
