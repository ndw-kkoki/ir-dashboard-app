"""
google_drive_client.py

Google DriveのOAuth認証およびサービスアカウント認証クラスモジュール。

必要ライブラリ:
    - google-api-python-client
    - google-auth
    - google-auth-httplib2
    - google-auth-oauthlib
    - pandas
    - openpyxl
"""

import os.path
import time
import ssl
from io import BytesIO

import pandas as pd

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    """
    指数バックオフでリトライを行うデコレータ関数
    
    Args:
        func: 実行する関数
        max_retries: 最大リトライ回数
        base_delay: 基本待機時間（秒）
    
    Returns:
        関数の実行結果
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except (ssl.SSLError, HttpError, Exception) as e:
            if attempt == max_retries:
                raise e
            
            # SSLエラーの場合は少し長めに待機
            if "SSL" in str(e) or "ssl" in str(e).lower():
                delay = base_delay * (2 ** attempt) + 1.0
            else:
                delay = base_delay * (2 ** attempt)
            
            print(f"接続エラー (試行 {attempt + 1}/{max_retries + 1}): {e}")
            print(f"{delay:.1f}秒後にリトライします...")
            time.sleep(delay)
    
    return None

class GoogleDriveClient:
    """
    Google Drive OAuth認証およびサービスアカウント認証クライアント
    """

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    def __init__(self, credentials_file='credentials.json', token_file='token.json', port=8080, use_service_account=None):
        """
        初期化と認証

        Args:
            credentials_file (str): OAuthクライアントID JSONファイル または サービスアカウントJSONファイル
            token_file (str): 認証情報保存ファイル (OAuth時のみ使用)
            port (int): ローカルサーバーポート (OAuth時のみ使用)
            use_service_account (bool): サービスアカウント認証を使用するか (None: 環境変数で判定)
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.port = port
        self._file_cache = {}  # ファイル一覧キャッシュ
        self._cache_expiry = {}  # キャッシュ有効期限
        
        # 本番環境判定 (環境変数やファイル存在で判定)
        if use_service_account is None:
            self.use_service_account = (
                os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is not None or
                os.environ.get('USE_SERVICE_ACCOUNT', 'false').lower() == 'true'
            )
        else:
            self.use_service_account = use_service_account
        
        self.service = self.authenticate()

    def authenticate(self):
        """
        OAuth認証またはサービスアカウント認証を行いDrive APIサービスを返す。

        Returns:
            Resource: Drive APIサービスオブジェクト
        """
        def _authenticate():
            if self.use_service_account:
                # サービスアカウント認証
                return self._authenticate_service_account()
            else:
                # OAuth認証
                return self._authenticate_oauth()
        
        return retry_with_backoff(_authenticate, max_retries=3, base_delay=2.0)
    
    def _authenticate_service_account(self):
        """
        サービスアカウント認証を行う
        
        Returns:
            Resource: Drive APIサービスオブジェクト
        """
        # 環境変数からサービスアカウントキーを取得
        if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            creds = service_account.Credentials.from_service_account_file(
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'], 
                scopes=self.SCOPES
            )
        else:
            # credentials_fileがサービスアカウントキーファイルの場合
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=self.SCOPES
            )
        
        service = build('drive', 'v3', credentials=creds)
        return service
    
    def _authenticate_oauth(self):
        """
        OAuth認証を行う
        
        Returns:
            Resource: Drive APIサービスオブジェクト
        """
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(
                    port=self.port, access_type='offline', prompt='consent')
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        return service

    def list_files_in_folder(self, folder_id, use_cache=True, cache_duration=300):
        """
        指定フォルダ内のファイル一覧を取得する（キャッシュ機能付き）。

        Args:
            folder_id (str): フォルダID
            use_cache (bool): キャッシュを使用するか
            cache_duration (int): キャッシュ有効期間（秒）

        Returns:
            list of dict: ファイル情報 {'id': ファイルID, 'name': ファイル名}
        """
        import time
        
        # キャッシュチェック
        if use_cache and folder_id in self._file_cache:
            if time.time() - self._cache_expiry.get(folder_id, 0) < cache_duration:
                return self._file_cache[folder_id]
        
        files = []
        
        def _list_files():
            nonlocal files
            files = []
            page_token = None

            while True:
                response = self.service.files().list(
                    q=f"'{folder_id}' in parents and trashed = false",
                    spaces='drive',
                    fields="nextPageToken, files(id, name)",
                    pageSize=1000,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()

                items = response.get('files', [])
                if not items:
                    print("フォルダ内にファイルが見つかりませんでした。")
                    break

                files.extend([{'name': item['name'], 'id': item['id']} for item in items])

                page_token = response.get('nextPageToken', None)
                if not page_token:
                    break
            
            return files
        
        # リトライ機能付きでファイル一覧を取得
        files = retry_with_backoff(_list_files, max_retries=3, base_delay=1.0)
        
        # filesを名前順にソート
        files.sort(key=lambda x: x['name'])

        # キャッシュに保存
        if use_cache:
            import time
            self._file_cache[folder_id] = files
            self._cache_expiry[folder_id] = time.time()

        return files

    def find_file_id(self, folder_id, filename):
        """
        指定フォルダ内でファイル名からファイルIDを取得する。

        Args:
            folder_id (str): フォルダID
            filename (str): ファイル名

        Returns:
            str: ファイルID
        """
        query = f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
        results = self.service.files().list(
            q=query,
            fields="files(id, name)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
        files = results.get('files', [])
        if not files:
            raise FileNotFoundError(f"File '{filename}' not found in folder '{folder_id}'")
        return files[0]['id']

    def download_file_as_bytes(self, file_id):
        """
        ファイルをBytesIOとしてダウンロードする。

        Args:
            file_id (str): ファイルID

        Returns:
            BytesIO: ダウンロードデータ
        """
        def _download():
            request = self.service.files().get_media(fileId=file_id)
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            return fh
        
        return retry_with_backoff(_download, max_retries=3, base_delay=1.0)

    def read_xlsx_from_drive(self, folder_id, filename):
        """
        Google Drive上の共有フォルダからxlsxファイルをpandasのExcelFileオブジェクトとして読み込む。

        Args:
            folder_id (str): Google DriveのフォルダID
            filename (str): ファイル名

        Returns:
            pandas.ExcelFile: Excelファイルオブジェクト
        """
        file_id = self.find_file_id(folder_id, filename)
        file_bytes = self.download_file_as_bytes(file_id)
        xls = pd.ExcelFile(file_bytes, engine='openpyxl')
        return xls


class DriveXlsxLoader:
    """
    Google Driveからxlsxファイルを簡単に読み込むためのラッパークラス
    """
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json', port=8080, use_service_account=None):
        """
        初期化
        
        Args:
            credentials_file (str): OAuthクライアントID JSONファイル または サービスアカウントJSONファイル
            token_file (str): 認証情報保存ファイル (OAuth時のみ使用)
            port (int): ローカルサーバーポート (OAuth時のみ使用)
            use_service_account (bool): サービスアカウント認証を使用するか
        """
        self.client = GoogleDriveClient(credentials_file, token_file, port, use_service_account)
    
    def load_dataframe_from_folder(self, folder_id, filename, sheet_name=0):
        """
        指定フォルダからxlsxファイルを読み込み、DataFrameとして返す
        
        Args:
            folder_id (str): Google DriveのフォルダID
            filename (str): ファイル名
            sheet_name (str or int): シート名またはインデックス
            
        Returns:
            pandas.DataFrame: 読み込んだデータ
        """
        try:
            xls = self.client.read_xlsx_from_drive(folder_id, filename)
            df = pd.read_excel(xls, sheet_name=sheet_name)
            return df
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            return pd.DataFrame()
    
    def list_files(self, folder_id, use_cache=True, cache_duration=300):
        """
        指定フォルダ内のファイル一覧を取得
        
        Args:
            folder_id (str): フォルダID
            use_cache (bool): キャッシュを使用するか
            cache_duration (int): キャッシュ有効期間（秒）
            
        Returns:
            list of dict: ファイル情報
        """
        return self.client.list_files_in_folder(folder_id, use_cache, cache_duration)
    
    def download_file(self, file_id):
        """
        指定ファイルIDのファイルをダウンロードしてバイトデータを返す
        
        Args:
            file_id (str): ファイルID
            
        Returns:
            bytes: ファイルのバイトデータ
        """
        try:
            file_bytes = self.client.download_file_as_bytes(file_id)
            return file_bytes.getvalue()
        except Exception as e:
            print(f"ファイルダウンロードエラー: {e}")
            raise
    
    def get_sheet_names(self, folder_id, filename):
        """
        指定ファイルのシート名一覧を取得
        
        Args:
            folder_id (str): Google DriveのフォルダID
            filename (str): ファイル名
            
        Returns:
            list: シート名のリスト
        """
        try:
            xls = self.client.read_xlsx_from_drive(folder_id, filename)
            return xls.sheet_names
        except Exception as e:
            print(f"シート名取得エラー: {e}")
            return []
    
    def download_text_file(self, file_id):
        """
        指定ファイルIDのテキストファイルをダウンロードして文字列として返す
        
        Args:
            file_id (str): ファイルID
            
        Returns:
            str: ファイルの内容（文字列）
        """
        try:
            file_bytes = self.client.download_file_as_bytes(file_id)
            # UTF-8でデコード、失敗したらShift_JISで試す
            try:
                content = file_bytes.getvalue().decode('utf-8')
            except UnicodeDecodeError:
                content = file_bytes.getvalue().decode('shift_jis')
            return content
        except Exception as e:
            print(f"テキストファイルダウンロードエラー: {e}")
            raise


if __name__ == "__main__":
    # 使用例
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.app_config import AppConfig

    folder_id = AppConfig.SEGMENT_DATA_FOLDER_ID
    filename = '1417.xlsx'

    loader = DriveXlsxLoader(credentials_file=AppConfig.CREDENTIALS_FILE, token_file=AppConfig.TOKEN_FILE)

    # フォルダ内ファイル一覧
    files = loader.list_files(folder_id)
    print("フォルダ内のファイル一覧:")
    for f in files:
        print(f" - {f['name']} ({f['id']})")

    # xlsxファイルを読み込み
    try:
        sheet_names = loader.get_sheet_names(folder_id, filename)
        print(f"シート名: {sheet_names}")

        for sheet_name in sheet_names:
            df = loader.load_dataframe_from_folder(folder_id, filename, sheet_name)
            print(f"Sheet: {sheet_name}")
            print(df.head())
    except Exception as e:
        print(f"エラー: {e}")
