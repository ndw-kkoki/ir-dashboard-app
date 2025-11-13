"""
base_component.py

UIコンポーネントの基底クラス
"""

from abc import ABC, abstractmethod
from dash import html


class BaseComponent(ABC):
    """UIコンポーネントの基底クラス"""
    
    def __init__(self, component_id: str, config: dict):
        """
        コンポーネントの初期化
        
        Args:
            component_id (str): コンポーネントの一意識別子
            config (dict): コンポーネント設定
        """
        self.component_id = component_id
        self.config = config
        self.title = config.get('title', 'Untitled')
        self.icon = config.get('icon', '')
    
    @abstractmethod
    def render(self) -> html.Div:
        """
        コンポーネントのレンダリング
        
        Returns:
            html.Div: レンダリングされたDashコンポーネント
        """
        pass
    
    def create_header(self, open_state: bool = True) -> html.Details:
        """
        共通のヘッダー部分を作成
        
        Args:
            open_state (bool): デフォルトの開閉状態
            
        Returns:
            html.Details: ヘッダー要素
        """
        return html.Details([
            html.Summary(
                f"{self.icon} {self.title}",
                style={
                    'padding': '15px',
                    'backgroundColor': '#f8f9fa',
                    'border': 'none',
                    'borderRadius': '10px 10px 0 0',
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'cursor': 'pointer',
                    'borderBottom': '1px solid #ddd',
                    'outline': 'none'
                }
            ),
            self.create_controls()
        ],
        open=open_state,
        style={
            'margin': '0',
            'border': 'none'
        })
    
    @abstractmethod
    def create_controls(self) -> html.Div:
        """
        コントロール部分の作成（サブクラスで実装）
        
        Returns:
            html.Div: コントロール要素
        """
        pass
    
    def create_container_style(self) -> dict:
        """
        コンテナの共通スタイルを作成
        
        Returns:
            dict: スタイル辞書
        """
        return {
            'height': '100%',
            'border': '1px solid #ddd',
            'borderRadius': '10px',
            'backgroundColor': 'white',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'display': 'flex',
            'flexDirection': 'column'
        }
