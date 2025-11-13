"""
chatbot_callbacks.py

チャットボット関連のコールバック関数
"""

from dash.dependencies import Input, Output, State
from dash import html
from typing import Any, Tuple, List
import logging

from services.chatbot_service import ChatbotService
from components.chatbot_card import ChatbotCard


class ChatbotCallbacks:
    """チャットボット関連のコールバック機能を提供するクラス"""
    
    def __init__(self, app, chatbot_service: ChatbotService):
        """
        チャットボットコールバックの初期化
        
        Args:
            app: Dashアプリケーションインスタンス
            chatbot_service (ChatbotService): チャットボットサービス
        """
        self.app = app
        self.chatbot_service = chatbot_service
        self.logger = logging.getLogger(__name__)
        self.register_callbacks()
    
    def register_callbacks(self):
        """すべてのコールバックを登録"""
        self.register_chatbot_message_callbacks()
        self.register_font_size_callbacks()
    
    def register_chatbot_message_callbacks(self):
        """チャットボットメッセージ関連コールバックを登録"""
        
        @self.app.callback(
            [Output('chatbot-messages-container', 'children'),
             Output('chatbot-input', 'value'),
             Output('chatbot-history-store', 'children')],
            [Input('chatbot-send-btn', 'n_clicks')],
            [State('chatbot-input', 'value'),
             State('chatbot-history-store', 'children'),
             State('chatbot-font-size-dropdown', 'value')]
        )
        def update_chatbot(send_clicks, user_input, history_json, font_size):
            """チャットボットの会話を更新"""
            return self.handle_chatbot_update(send_clicks, user_input, history_json, font_size)
    
    def register_font_size_callbacks(self):
        """フォントサイズ変更コールバックを登録"""
        
        @self.app.callback(
            Output('chatbot-messages-container', 'children', allow_duplicate=True),
            [Input('chatbot-font-size-dropdown', 'value')],
            [State('chatbot-history-store', 'children')],
            prevent_initial_call=True
        )
        def update_chatbot_font_size(font_size, history_json):
            """チャットボットのフォントサイズを変更"""
            return self.handle_font_size_update(font_size, history_json)
    
    def handle_chatbot_update(self, send_clicks: int, user_input: str, history_json: str, font_size: int) -> Tuple[List[Any], str, str]:
        """
        チャットボット更新処理
        
        Args:
            send_clicks (int): 送信ボタンクリック回数
            user_input (str): ユーザー入力
            history_json (str): チャット履歴JSON
            font_size (int): フォントサイズ
            
        Returns:
            Tuple[List[Any], str, str]: (メッセージ要素リスト, 入力値クリア, 更新された履歴JSON)
        """
        try:
            # ChatbotCardインスタンスを作成（設定は仮）
            chatbot_card = ChatbotCard('chatbot', {'title': 'チャットボット', 'icon': '💬'})
            
            # 初期状態の処理
            if not send_clicks:
                initial_messages = [chatbot_card.create_initial_message()]
                return initial_messages, '', '[]'
            
            # 入力バリデーション
            if not user_input or not self.chatbot_service.validate_message(user_input):
                # 履歴をそのまま表示
                message_elements = chatbot_card.format_chat_history(history_json, font_size)
                return message_elements, '', history_json
            
            # ボットの応答を生成
            bot_response = self.chatbot_service.get_response(user_input.strip())
            
            # 履歴を更新
            updated_history = chatbot_card.add_message_to_history(history_json, user_input, bot_response)
            
            # メッセージ表示要素を生成
            message_elements = chatbot_card.format_chat_history(updated_history, font_size)
            
            return message_elements, '', updated_history
            
        except Exception as e:
            self.logger.error(f"チャットボット更新エラー: {e}")
            error_message = [html.P("エラーが発生しました", style={'color': 'red'})]
            return error_message, '', history_json or '[]'
    
    def handle_font_size_update(self, font_size: int, history_json: str) -> List[Any]:
        """
        フォントサイズ更新処理
        
        Args:
            font_size (int): 新しいフォントサイズ
            history_json (str): チャット履歴JSON
            
        Returns:
            List[Any]: 更新されたメッセージ要素リスト
        """
        try:
            # ChatbotCardインスタンスを作成（設定は仮）
            chatbot_card = ChatbotCard('chatbot', {'title': 'チャットボット', 'icon': '💬'})
            
            # フォントサイズを適用して履歴を再描画
            return chatbot_card.format_chat_history(history_json, font_size)
            
        except Exception as e:
            self.logger.error(f"フォントサイズ更新エラー: {e}")
            return [html.P("エラーが発生しました", style={'color': 'red'})]
