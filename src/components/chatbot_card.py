"""
chatbot_card.py

チャットボットカードコンポーネント
"""

import json
import datetime
from dash import html, dcc
from typing import List, Dict
from .base_component import BaseComponent


class ChatbotCard(BaseComponent):
    """チャットボットカードコンポーネント"""
    
    def __init__(self, component_id: str, config: dict, font_size_options: List[Dict] = None, default_font_size: int = 14, placeholder: str = "", max_history: int = 10):
        """
        チャットボットカードの初期化
        
        Args:
            component_id (str): コンポーネントID
            config (dict): コンポーネント設定
            font_size_options (List[Dict]): フォントサイズオプション
            default_font_size (int): デフォルトフォントサイズ
            placeholder (str): 入力欄のプレースホルダー
            max_history (int): 最大履歴保持数
        """
        super().__init__(component_id, config)
        self.font_size_options = font_size_options or []
        self.default_font_size = default_font_size
        self.placeholder = placeholder
        self.max_history = max_history
    
    def render(self) -> html.Div:
        """
        チャットボットカードをレンダリング
        
        Returns:
            html.Div: レンダリングされたコンポーネント
        """
        return html.Div([
            html.Div([
                self.create_header(),
                self.create_chat_area()
            ], style=self.create_container_style()),
            
            # チャット履歴を保存するための隠しDiv
            html.Div(id=f'{self.component_id}-history-store', style={'display': 'none'}, children='[]')
        ], style={'width': '100%', 'height': '100%'})
    
    def create_controls(self) -> html.Div:
        """
        コントロール部分を作成
        
        Returns:
            html.Div: コントロール要素
        """
        return html.Div([
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
    
    def create_chat_area(self) -> html.Div:
        """
        チャット表示エリアを作成
        
        Returns:
            html.Div: チャットエリア
        """
        return html.Div([
            # チャット履歴表示エリア
            html.Div(
                id=f'{self.component_id}-messages-container',
                style={
                    'flex': '1',
                    'border': '1px solid #ddd',
                    'backgroundColor': '#f9f9f9',
                    'padding': '15px',
                    'margin': '0 10px 10px 10px',
                    'overflow': 'auto',
                    'maxHeight': '800px',
                    'minHeight': '200px'
                },
                children=[self.create_initial_message()]
            ),
            
            # 入力エリア
            self.create_input_area()
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'flex': '1'
        })
    
    def create_initial_message(self) -> html.P:
        """
        初期メッセージを作成
        
        Returns:
            html.P: 初期メッセージ
        """
        return html.P(
            "こんにちは！表示中のデータについて何でもお聞きください。",
            style={
                'color': '#666',
                'fontSize': '14px',
                'margin': '0',
                'padding': '10px',
                'backgroundColor': '#e3f2fd',
                'borderRadius': '10px',
                'marginBottom': '10px'
            }
        )
    
    def create_input_area(self) -> html.Div:
        """
        入力エリアを作成
        
        Returns:
            html.Div: 入力エリア
        """
        return html.Div([
            html.Div([
                dcc.Textarea(
                    id=f'{self.component_id}-input',
                    placeholder=self.placeholder,
                    style={
                        'width': '100%',
                        'height': '100px',
                        'minHeight': '60px',
                        'maxHeight': '300px',
                        'resize': 'vertical',
                        'border': '1px solid #ddd',
                        'borderRadius': '5px',
                        'padding': '10px',
                        'fontSize': '14px',
                        'boxSizing': 'border-box',
                        'fontFamily': 'inherit'
                    },
                    value=''
                )
            ], style={
                'flex': '1',
                'display': 'flex',
                'alignItems': 'flex-end',
                'marginRight': '10px'
            }),
            
            html.Div([
                html.Button(
                    "送信",
                    id=f'{self.component_id}-send-btn',
                    n_clicks=0,
                    style={
                        'height': '40px',
                        'width': '80px',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'backgroundColor': "#4CAF50",
                        'color': 'white',
                        'border': 'none',
                        'fontWeight': 'bold',
                        'boxSizing': 'border-box'
                    }
                )
            ], style={
                'flex': '0 0 80px',
                'display': 'flex',
                'alignItems': 'flex-end'
            })
        ], style={
            'display': 'flex',
            'padding': '0 10px 10px 10px',
            'alignItems': 'flex-end',
            'gap': '0'
        })
    
    def create_message_element(self, message: Dict, font_size: int) -> html.Div:
        """
        メッセージ要素を作成
        
        Args:
            message (Dict): メッセージデータ
            font_size (int): フォントサイズ
            
        Returns:
            html.Div: メッセージ要素
        """
        if message['type'] == 'user':
            return self.create_user_message(message, font_size)
        else:
            return self.create_bot_message(message, font_size)
    
    def create_user_message(self, message: Dict, font_size: int) -> html.Div:
        """
        ユーザーメッセージ要素を作成
        
        Args:
            message (Dict): メッセージデータ
            font_size (int): フォントサイズ
            
        Returns:
            html.Div: ユーザーメッセージ要素
        """
        return html.Div([
            html.P(
                message['content'],
                style={
                    'fontSize': f'{font_size}px',
                    'margin': '0',
                    'padding': '10px',
                    'backgroundColor': '#2196F3',
                    'color': 'white',
                    'borderRadius': '10px',
                    'marginBottom': '5px',
                    'marginLeft': '20%',
                    'textAlign': 'right'
                }
            ),
            html.P(
                f"送信時刻: {message['timestamp'][:16].replace('T', ' ')}",
                style={
                    'fontSize': f'{max(8, font_size-4)}px',
                    'color': '#999',
                    'margin': '0 0 10px 0',
                    'textAlign': 'right'
                }
            )
        ])
    
    def create_bot_message(self, message: Dict, font_size: int) -> html.Div:
        """
        ボットメッセージ要素を作成
        
        Args:
            message (Dict): メッセージデータ
            font_size (int): フォントサイズ
            
        Returns:
            html.Div: ボットメッセージ要素
        """
        return html.Div([
            html.P(
                f"🤖 {message['content']}",
                style={
                    'fontSize': f'{font_size}px',
                    'margin': '0',
                    'padding': '10px',
                    'backgroundColor': '#e3f2fd',
                    'borderRadius': '10px',
                    'marginBottom': '5px',
                    'marginRight': '20%'
                }
            ),
            html.P(
                f"応答時刻: {message['timestamp'][:16].replace('T', ' ')}",
                style={
                    'fontSize': f'{max(8, font_size-4)}px',
                    'color': '#999',
                    'margin': '0 0 10px 0'
                }
            )
        ])
    
    def format_chat_history(self, history_json: str, font_size: int) -> List[html.Div]:
        """
        チャット履歴をフォーマット
        
        Args:
            history_json (str): JSON形式の履歴データ
            font_size (int): フォントサイズ
            
        Returns:
            List[html.Div]: フォーマット済みメッセージ要素のリスト
        """
        try:
            history = json.loads(history_json) if history_json else []
        except:
            history = []
        
        if not history:
            return [self.create_initial_message()]
        
        message_elements = []
        for message in history:
            message_elements.append(self.create_message_element(message, font_size))
        
        return message_elements
    
    def add_message_to_history(self, history_json: str, user_input: str, bot_response: str) -> str:
        """
        メッセージを履歴に追加
        
        Args:
            history_json (str): JSON形式の現在の履歴
            user_input (str): ユーザー入力
            bot_response (str): ボット応答
            
        Returns:
            str: 更新されたJSON形式の履歴
        """
        try:
            history = json.loads(history_json) if history_json else []
        except:
            history = []
        
        # ユーザーメッセージを追加
        user_message = {
            'type': 'user',
            'content': user_input.strip(),
            'timestamp': datetime.datetime.now().isoformat()
        }
        history.append(user_message)
        
        # ボットメッセージを追加
        bot_message = {
            'type': 'bot',
            'content': bot_response,
            'timestamp': datetime.datetime.now().isoformat()
        }
        history.append(bot_message)
        
        # 履歴の上限を管理
        if len(history) > self.max_history * 2:  # ユーザーとボットで2倍
            history = history[-self.max_history * 2:]
        
        return json.dumps(history)
