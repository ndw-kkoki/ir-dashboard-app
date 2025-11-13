"""
drive_service.py

Google Drive操作を管理するサービス
"""

import concurrent.futures
import logging
from typing import List, Dict, Optional, Tuple
from utils.drive_xlsx_loader import DriveXlsxLoader
from .file_service import FileService


class DriveService:
    """Google Drive操作を提供するサービスクラス"""
    
    def __init__(self, credentials_file: str, token_file: str, use_service_account: bool = None):
        """
        Google Driveサービスの初期化
        
        Args:
            credentials_file (str): 認証情報ファイルパス
            token_file (str): トークンファイルパス
            use_service_account (bool): サービスアカウント認証を使用するか
        """
        self.logger = logging.getLogger(__name__)
        self.file_service = FileService()
        self.drive_loader = None
        self.connection_status = "disconnected"
        
        # 各フォルダのファイルキャッシュ
        self.segment_files = []
        self.revenue_files = []
        self.ai_summary_files = []
        
        # Google Drive接続を試行
        try:
            self.drive_loader = DriveXlsxLoader(
                credentials_file=credentials_file,
                token_file=token_file,
                use_service_account=use_service_account
            )
            self.connection_status = "connected"
            self.logger.info("Google Drive接続成功")
        except Exception as e:
            self.logger.error(f"Google Drive接続エラー: {e}")
            self.connection_status = "error"
    
    def is_connected(self) -> bool:
        """
        Google Driveとの接続状態を確認
        
        Returns:
            bool: 接続されている場合True
        """
        return self.connection_status == "connected" and self.drive_loader is not None
    
    def load_files_async(self, folder_ids: Dict[str, str], timeout: int = 30) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        複数フォルダのファイルを非同期で並列取得
        
        Args:
            folder_ids (Dict[str, str]): フォルダID辞書 {'segment': id, 'revenue': id, 'ai_summary': id}
            timeout (int): タイムアウト時間（秒）
            
        Returns:
            Tuple[List[Dict], List[Dict], List[Dict]]: (セグメントファイル, 収益ファイル, AI要約ファイル)
        """
        if not self.is_connected():
            return [], [], []
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # 並列処理でファイル一覧を取得
                segment_future = executor.submit(
                    self.drive_loader.list_files, 
                    folder_ids.get('segment', ''), 
                    True, 300
                )
                revenue_future = executor.submit(
                    self.drive_loader.list_files, 
                    folder_ids.get('revenue', ''), 
                    True, 300
                )
                ai_summary_future = executor.submit(
                    self.drive_loader.list_files, 
                    folder_ids.get('ai_summary', ''), 
                    True, 300
                )
                
                # 結果を取得
                segment_files = segment_future.result(timeout=timeout)
                revenue_files = revenue_future.result(timeout=timeout)
                ai_summary_files = ai_summary_future.result(timeout=timeout)
                
                # ファイルをフィルタリング
                self.segment_files = self.file_service.filter_files_by_extension(segment_files, '.xlsx')
                self.revenue_files = self.file_service.filter_files_by_extension(revenue_files, '.xlsx')
                ai_summary_txt_files = self.file_service.filter_files_by_extension(ai_summary_files, '.txt')
                
                self.logger.info(f"ファイル取得成功: セグメント{len(self.segment_files)}件, 収益{len(self.revenue_files)}件, AI要約{len(ai_summary_txt_files)}件")
                
                return self.segment_files, self.revenue_files, ai_summary_txt_files
                
        except concurrent.futures.TimeoutError:
            self.logger.error(f"Google Drive接続タイムアウト: {timeout}秒以内に応答がありませんでした")
            return [], [], []
        except Exception as e:
            self.logger.error(f"Google Drive接続エラー: {type(e).__name__}: {e}")
            return [], [], []
    
    def get_dropdown_options(self, files: List[Dict]) -> Tuple[List[Dict], Optional[str]]:
        """
        ファイルリストからドロップダウンオプションとデフォルト値を取得
        
        Args:
            files (List[Dict]): ファイルリスト
            
        Returns:
            Tuple[List[Dict], Optional[str]]: (オプションリスト, デフォルト値)
        """
        options = self.file_service.create_dropdown_options(files, remove_extension=True)
        default_value = options[0]['value'] if options else None
        return options, default_value
    
    def download_file_content(self, file_id: str) -> Optional[bytes]:
        """
        ファイルのバイナリコンテンツをダウンロード
        
        Args:
            file_id (str): ダウンロードするファイルID
            
        Returns:
            Optional[bytes]: ファイルコンテンツ、エラーの場合None
        """
        if not self.is_connected() or not self.file_service.validate_file_id(file_id):
            return None
        
        try:
            return self.drive_loader.download_file(file_id)
        except Exception as e:
            self.logger.error(f"ファイルダウンロードエラー: {e}")
            return None
    
    def download_text_content(self, file_id: str) -> Optional[str]:
        """
        テキストファイルの内容をダウンロード
        
        Args:
            file_id (str): ダウンロードするファイルID
            
        Returns:
            Optional[str]: テキストコンテンツ、エラーの場合None
        """
        if not self.is_connected() or not self.file_service.validate_file_id(file_id):
            return None
        
        try:
            return self.drive_loader.download_text_file(file_id)
        except Exception as e:
            self.logger.error(f"テキストファイルダウンロードエラー: {e}")
            return None
    

    
    def get_connection_info(self) -> Dict[str, str]:
        """
        接続情報を取得
        
        Returns:
            Dict[str, str]: 接続情報
        """
        return {
            'status': self.connection_status,
            'segment_count': str(len(self.segment_files)),
            'revenue_count': str(len(self.revenue_files)),
            'loader_available': str(self.drive_loader is not None)
        }
