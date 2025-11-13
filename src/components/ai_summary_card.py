"""
ai_summary_card.py

AI要約表示カードコンポーネント
"""

from dash import html, dcc
from typing import List, Dict
from .base_component import BaseComponent


class AISummaryCard(BaseComponent):
    """AI要約表示カードコンポーネント"""
    
    def __init__(self, component_id: str, config: dict, file_options: List[Dict] = None, font_size_options: List[Dict] = None, default_font_size: int = 14):
        """
        AI要約カードの初期化
        
        Args:
            component_id (str): コンポーネントID
            config (dict): コンポーネント設定
            file_options (List[Dict]): ファイル選択オプション
            font_size_options (List[Dict]): フォントサイズオプション
            default_font_size (int): デフォルトフォントサイズ
        """
        super().__init__(component_id, config)
        self.file_options = file_options or []
        self.font_size_options = font_size_options or []
        self.default_font_size = default_font_size
    
    def render(self) -> html.Div:
        """
        AI要約カードをレンダリング
        
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
                html.Label("要約ファイル:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    options=self.file_options,
                    value=self.file_options[0]['value'] if self.file_options else None,
                    id=f'{self.component_id}-file-dropdown',
                    placeholder="読み込み中...",
                    style={'marginBottom': '10px'}
                )
            ], style={'flex': '1', 'marginRight': '10px'}),
            
            # フォントサイズ設定
            html.Div([
                html.Label("フォントサイズ:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id=f'{self.component_id}-font-size-dropdown',
                    options=self.font_size_options,
                    value=self.default_font_size,
                    style={'marginBottom': '10px'}
                )
            ], style={'flex': '1'})
        ], style={
            'display': 'flex', 
            'padding': '10px', 
            'backgroundColor': '#fdfdfd'
        })
    
    def create_content_area(self) -> html.Div:
        """
        テキスト表示エリアを作成
        
        Returns:
            html.Div: テキスト表示エリア
        """
        return html.Div(
            id=f'{self.component_id}-text-container',
            style={
                'flex': '1',
                'border': '1px solid #ddd',
                'borderRadius': '0 0 10px 10px',
                'backgroundColor': '#f9f9f9',
                'padding': '15px',
                'margin': '0 10px 10px 10px',
                'overflow': 'auto',
                'maxHeight': '800px'
            },
            children=[html.P("読み込み中...", style={'color': '#666', 'fontSize': '16px', 'fontFamily': 'Arial, sans-serif'})]
        )
    
    def format_text_content(self, text_content: str, font_size: int) -> List[html.P]:
        """
        テキストコンテンツをフォーマット
        
        Args:
            text_content (str): テキストコンテンツ
            font_size (int): フォントサイズ
            
        Returns:
            List[html.P]: フォーマット済みテキスト要素のリスト
        """
        if not text_content:
            return [html.P("テキストが空です", style={'color': '#666', 'fontSize': '16px', 'fontFamily': 'Arial, sans-serif'})]
        
        # テキストを段落に分割
        paragraphs = text_content.split('\n\n')
        
        text_elements = []
        for paragraph in paragraphs:
            if paragraph.strip():  # 空でない段落のみ
                text_elements.append(
                    html.P(
                        paragraph.strip(),
                        style={
                            'fontSize': f'{font_size}px',
                            'lineHeight': '1.6',
                            'marginBottom': '15px',
                            'color': '#333',
                            'whiteSpace': 'pre-wrap',  # 改行を保持
                            'fontFamily': 'Arial, sans-serif'
                        }
                    )
                )
        
        return text_elements if text_elements else [html.P("テキストが空です", style={'color': '#666', 'fontSize': '16px', 'fontFamily': 'Arial, sans-serif'})]
