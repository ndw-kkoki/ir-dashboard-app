"""
file_service.py

ファイル操作関連の機能を提供するサービス
"""

from typing import List, Dict, Optional
import logging


class FileService:
    """ファイル操作機能を提供するサービスクラス"""
    
    def __init__(self):
        """ファイルサービスの初期化"""
        self.logger = logging.getLogger(__name__)
    
    def filter_files_by_extension(self, files: List[Dict], extension: str) -> List[Dict]:
        """
        ファイルリストを拡張子でフィルタリング
        
        Args:
            files (List[Dict]): ファイルリスト
            extension (str): 拡張子（例: '.xlsx', '.txt'）
            
        Returns:
            List[Dict]: フィルタリングされたファイルリスト
        """
        try:
            return [f for f in files if f.get('name', '').endswith(extension)]
        except Exception as e:
            self.logger.error(f"ファイルフィルタリングエラー: {e}")
            return []
    
    def create_dropdown_options(self, files: List[Dict], remove_extension: bool = True) -> List[Dict]:
        """
        ファイルリストからドロップダウンオプションを作成
        
        Args:
            files (List[Dict]): ファイルリスト
            remove_extension (bool): 拡張子を除去するかどうか
            
        Returns:
            List[Dict]: ドロップダウンオプション
        """
        try:
            options = []
            for file in files:
                name = file.get('name', '')
                file_id = file.get('id', '')
                
                if not name or not file_id:
                    continue
                
                # 拡張子を除去
                if remove_extension and '.' in name:
                    display_name = name.rsplit('.', 1)[0]
                else:
                    display_name = name
                
                options.append({
                    'label': display_name,
                    'value': file_id
                })
            
            return options
        except Exception as e:
            self.logger.error(f"ドロップダウンオプション作成エラー: {e}")
            return []
    

    
    def validate_file_id(self, file_id: str) -> bool:
        """
        ファイルIDの妥当性をチェック
        
        Args:
            file_id (str): チェック対象のファイルID
            
        Returns:
            bool: ファイルIDが妥当な場合True
        """
        if not file_id or not isinstance(file_id, str):
            return False
        
        # Google DriveのファイルIDは通常33文字程度の英数字
        if len(file_id) < 20 or len(file_id) > 50:
            return False
        
        return True
    
    def sort_files_by_name(self, files: List[Dict], reverse: bool = False) -> List[Dict]:
        """
        ファイルリストを名前順でソート
        
        Args:
            files (List[Dict]): ファイルリスト
            reverse (bool): 降順でソートするかどうか
            
        Returns:
            List[Dict]: ソートされたファイルリスト
        """
        try:
            return sorted(files, key=lambda x: x.get('name', ''), reverse=reverse)
        except Exception as e:
            self.logger.error(f"ファイルソートエラー: {e}")
            return files
    
    def get_file_extension(self, filename: str) -> str:
        """
        ファイル名から拡張子を取得
        
        Args:
            filename (str): ファイル名
            
        Returns:
            str: 拡張子（ドット付き）
        """
        if not filename or '.' not in filename:
            return ''
        
        return '.' + filename.rsplit('.', 1)[1].lower()
    
    def is_valid_filename(self, filename: str) -> bool:
        """
        ファイル名の妥当性をチェック
        
        Args:
            filename (str): チェック対象のファイル名
            
        Returns:
            bool: ファイル名が妥当な場合True
        """
        if not filename or not isinstance(filename, str):
            return False
        
        # 無効な文字をチェック
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in filename for char in invalid_chars):
            return False
        
        # 長さチェック
        if len(filename) > 255:
            return False
        
        return True
