"""
layout_config.py

レイアウト設定クラス
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class LayoutConfig:
    """レイアウト設定クラス"""
    
    # グリッドレイアウト設定
    GRID_LAYOUTS: Dict[str, List[Dict[str, Any]]] = None
    
    # カードサイズ設定
    CARD_HEIGHT: int = 20
    CARD_WIDTH_FULL: int = 12
    CARD_WIDTH_HALF: int = 6
    
    # レスポンシブブレイクポイント
    BREAKPOINTS: Dict[str, int] = None
    
    # グリッド設定
    GRID_COLS: Dict[str, int] = None
    ROW_HEIGHT: int = 30
    
    def __post_init__(self):
        """初期化後の設定"""
        if self.GRID_LAYOUTS is None:
            self.GRID_LAYOUTS = {
                'lg': [
                    {"i": "0", "x": 0, "y": 0, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT},  # セグメントデータ
                    {"i": "1", "x": self.CARD_WIDTH_HALF, "y": 0, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT},  # 収益動向
                    {"i": "2", "x": 0, "y": self.CARD_HEIGHT, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT}, # AI要約
                    {"i": "3", "x": self.CARD_WIDTH_HALF, "y": self.CARD_HEIGHT, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT}  # チャットボット
                ],
                'md': [
                    {"i": "0", "x": 0, "y": 0, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT},
                    {"i": "1", "x": self.CARD_WIDTH_HALF, "y": 0, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT},
                    {"i": "2", "x": 0, "y": self.CARD_HEIGHT, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT},
                    {"i": "3", "x": self.CARD_WIDTH_HALF, "y": self.CARD_HEIGHT, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT}
                ],
                'sm': [
                    {"i": "0", "x": 0, "y": 0, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT},
                    {"i": "1", "x": self.CARD_WIDTH_HALF, "y": 0, "w": self.CARD_WIDTH_HALF, "h": self.CARD_HEIGHT},
                    {"i": "2", "x": 0, "y": self.CARD_HEIGHT, "w": self.CARD_WIDTH_FULL, "h": self.CARD_HEIGHT},
                    {"i": "3", "x": 0, "y": self.CARD_HEIGHT * 2, "w": self.CARD_WIDTH_FULL, "h": self.CARD_HEIGHT}
                ]
            }
        
        if self.BREAKPOINTS is None:
            self.BREAKPOINTS = {
                'lg': 1200,
                'md': 996,
                'sm': 768,
                'xs': 480,
                'xxs': 0
            }
        
        if self.GRID_COLS is None:
            self.GRID_COLS = {
                'lg': 12,
                'md': 12, 
                'sm': 12,
                'xs': 6,
                'xxs': 4
            }
    
    def get_layout_for_screen(self, screen_size: str) -> List[Dict[str, Any]]:
        """
        画面サイズに応じたレイアウトを取得
        
        Args:
            screen_size (str): 画面サイズ ('lg', 'md', 'sm', 'xs', 'xxs')
            
        Returns:
            List[Dict[str, Any]]: レイアウト設定
        """
        return self.GRID_LAYOUTS.get(screen_size, self.GRID_LAYOUTS['lg'])
    
    def create_responsive_layout(self, 
                               component_count: int = 4,
                               columns_per_row: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """
        レスポンシブレイアウトを動的に作成
        
        Args:
            component_count (int): コンポーネント数
            columns_per_row (int): 1行あたりのカラム数
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: レスポンシブレイアウト設定
        """
        layouts = {}
        
        for screen_size, cols in self.GRID_COLS.items():
            layout = []
            
            # 画面サイズに応じてカラム数を調整
            if screen_size in ['xs', 'xxs']:
                cols_per_row = 1  # 小画面では1列
                card_width = cols
            elif screen_size == 'sm':
                cols_per_row = min(2, columns_per_row)  # 中画面では最大2列
                card_width = cols // cols_per_row
            else:
                cols_per_row = columns_per_row  # 大画面では指定列数
                card_width = cols // cols_per_row
            
            # 各コンポーネントの位置を計算
            for i in range(component_count):
                row = i // cols_per_row
                col = i % cols_per_row
                
                layout.append({
                    "i": str(i),
                    "x": col * card_width,
                    "y": row * self.CARD_HEIGHT,
                    "w": card_width,
                    "h": self.CARD_HEIGHT
                })
            
            layouts[screen_size] = layout
        
        return layouts
    
    def get_component_style(self, component_type: str = 'default') -> Dict[str, Any]:
        """
        コンポーネントタイプに応じたスタイルを取得
        
        Args:
            component_type (str): コンポーネントタイプ
            
        Returns:
            Dict[str, Any]: スタイル設定
        """
        base_style = {
            'width': '100%',
            'height': '100%',
            'border': '1px solid #ddd',
            'borderRadius': '10px',
            'backgroundColor': 'white',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'display': 'flex',
            'flexDirection': 'column'
        }
        
        # コンポーネントタイプ別の追加スタイル
        type_styles = {
            'data_card': {
                'borderColor': '#e3f2fd'
            },
            'ai_summary': {
                'borderColor': '#f3e5f5'
            },
            'chatbot': {
                'borderColor': '#e8f5e8'
            },
            'chart': {
                'borderColor': '#fff3e0'
            }
        }
        
        # ベーススタイルにタイプ別スタイルを適用
        if component_type in type_styles:
            base_style.update(type_styles[component_type])
        
        return base_style
    
    def get_responsive_props(self) -> Dict[str, Any]:
        """
        ResponsiveGridLayoutのプロパティを取得
        
        Returns:
            Dict[str, Any]: レスポンシブグリッドのプロパティ
        """
        return {
            'layouts': self.GRID_LAYOUTS,
            'breakpoints': self.BREAKPOINTS,
            'margin': [10, 10],
            'containerPadding': [10, 10],
            'isDraggable': True,
            'isResizable': True,
            'compactType': 'vertical',
            'preventCollision': False
        }
